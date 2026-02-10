import time
import threading
from decimal import Decimal
from typing import Dict
import signal
import sys
import hashlib
import os

from django.utils import timezone

from ..strategies.grid_strategy import GridStrategy, GridStrategyConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.config import LiveExecEngineConfig
from nautilus_trader.config import LiveRiskEngineConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import MessageBusConfig
from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.config import LiveDataEngineConfig
from nautilus_trader.config import CacheConfig
from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceExecClientConfig
from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory, BinanceLiveExecClientFactory
from nautilus_trader.model.identifiers import InstrumentId, TraderId

# Configuration constants
GRID_OFFSET = Decimal('0.08')
GRID_LEVELS = 15
DEFAULT_QUANTITY = Decimal('0.040')
MIN_QUANTITY = Decimal('0.001')  # More realistic minimum

# Global process tracking
_active_processes: Dict[int, threading.Thread] = {}
_process_lock = threading.Lock()


def _setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        _stop_all_bots()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def _stop_all_bots():
    """Stop all running bots"""
    with _process_lock:
        for user_id, thread in list(_active_processes.items()):
            if thread.is_alive():
                print(f"Stopping bot for user {user_id}...")
                # We can't directly stop threads, but we can mark them for shutdown
                # through the database
        _active_processes.clear()

def _run_live_bot(user_id: int, username: str, config_data: dict):
    """Main live bot runner function - COMPLETELY ISOLATED PER USER"""
    import os
    import django
    
    # Setup Django with unique environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    
    # Generate SHORTER unique session ID (4 chars max for live)
    session_id = hashlib.md5(f"LIVE_{user_id}_{username}_{time.time()}_{os.getpid()}".encode()).hexdigest()[:4]
    os.environ['USER_SESSION_ID'] = session_id
    
    django.setup()

    from ...models import BotConfig, LiveTrade, LiveBotLog

    # Extract configuration
    instrument = config_data['instrument']
    custom_qty_str = config_data.get('custom_quantity')
    quantity = Decimal(custom_qty_str) if custom_qty_str else DEFAULT_QUANTITY
    quantity = max(quantity, MIN_QUANTITY)
    api_key = config_data['api_key']
    api_secret = config_data['api_secret']

    instrument_id_str = f"{instrument}-PERP.BINANCE"
    instrument_id = InstrumentId.from_str(instrument_id_str)

    def log(message: str, level: str = "INFO"):
        """Log message to database with user isolation"""
        try:
            LiveBotLog.objects.create(
                user_id=user_id,
                message=f"[{session_id}] {str(message).strip()[:950]}",
                level=level.upper()
            )
            # Cleanup old logs (keep last 500 per user)
            count = LiveBotLog.objects.filter(user_id=user_id).count()
            if count > 500:
                excess_ids = LiveBotLog.objects.filter(user_id=user_id)\
                    .order_by('timestamp')\
                    .values_list('id', flat=True)[:count - 500]
                LiveBotLog.objects.filter(id__in=list(excess_ids)).delete()
        except Exception as e:
            print(f"[{session_id}] LOG ERROR: {e} | {message}")

    log(f"[INIT] Initializing Nautilus node for {instrument} (LIVE)...")

    # Configure instrument provider
    instrument_provider_config = InstrumentProviderConfig(
        load_ids=(instrument_id_str,),
        load_all=False
    )

    # Configure trading node with trader ID that CONTAINS A HYPHEN
    # Format: LIVE-{user_id}-{session_id}
    trader_id = f"LIVE-{user_id}-{session_id}"
    if len(trader_id) > 20:  # Keep it reasonable
        trader_id = f"LIVE-{user_id}-{session_id[:2]}"
    
    node_config = TradingNodeConfig(
        trader_id=TraderId(trader_id),  # MUST contain hyphen!
        logging=LoggingConfig(
            log_level="INFO",
            log_colors=True,
            bypass_logging=False
        ),
        cache=CacheConfig(
            timestamps_as_iso8601=True,
            tick_capacity=100_000,
            bar_capacity=20_000
        ),
        message_bus=MessageBusConfig(),
        data_engine=LiveDataEngineConfig(),  # Simplified - no invalid parameters
        risk_engine=LiveRiskEngineConfig(
            max_order_submit_rate="50/00:00:01",  # Lower rate for live
            max_order_modify_rate="50/00:00:01",
            bypass=False
        ),
        exec_engine=LiveExecEngineConfig(
            reconciliation=True,
            reconciliation_lookback_mins=120  # Longer lookback for live
        ),
        data_clients={
            "BINANCE": BinanceDataClientConfig(
                api_key=api_key,
                api_secret=api_secret,
                account_type=BinanceAccountType.USDT_FUTURES,
                testnet=False,  # LIVE trading
                instrument_provider=instrument_provider_config,
                use_agg_trade_ticks=True,
                ws_request_limit=10,  # Limit WebSocket requests
            )
        },
        exec_clients={
            "BINANCE": BinanceExecClientConfig(
                api_key=api_key,
                api_secret=api_secret,
                account_type=BinanceAccountType.USDT_FUTURES,
                testnet=False,  # LIVE trading
                instrument_provider=instrument_provider_config,
                use_gtd=False,
                post_only=True,  # Safer for live trading
                check_order_limits=True,
            )
        },
    )

    # Create and configure trading node
    node = TradingNode(config=node_config)

    # Configure strategy with conservative settings for live trading
    strategy_config = GridStrategyConfig(
        instrument_id=instrument_id,
        user_id=user_id,  # Pass user_id for isolation
        grid_levels=GRID_LEVELS,
        order_quantity=quantity,
        grid_offset=float(GRID_OFFSET),
        grid_profit=1.2,
        recenter_drift_threshold=0.03,
        recenter_interval_seconds=300,
        breakout_threshold=0.05,  # Slightly tighter for live
        trailing_stop_threshold=0.06,  # Tighter for live
        max_drawdown_percent=0.10,  # More conservative for live
        max_long_notional=Decimal("500"),  # Lower limits for live
        max_short_notional=Decimal("500"),
        max_total_notional=Decimal("800"),
        margin_safety_threshold=0.50,  # More conservative
        volatility_adapt_offset=True,
        enable_auto_resume=True,
        resume_cooldown_minutes=45,  # Longer cooldown for live
        resume_price_tolerance=0.02,  # Tighter tolerance
        enable_breakout_stop=True,
        enable_exposure_limits=True,
        enable_margin_monitoring=True,
        enable_trailing_stop=True,
        enable_max_drawdown=True,
        stop_loss_percent=1.5,  # Tighter stop loss for live
        max_position_multiplier=2.0,  # More conservative
        trend_detection_period=20,
        asymmetric_profit_factor=1.3,  # Less aggressive for live
        consider_funding_rate=True,
        dynamic_grid_adjustment=True,
        min_grid_levels=5,
        max_grid_levels=25,  # Fewer levels for live
        order_validation_distance=0.002,  # More distance for safety
    )

    strategy = GridStrategy(config=strategy_config)
    node.trader.add_strategy(strategy)
    
    # Add client factories
    node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
    node.add_exec_client_factory("BINANCE", BinanceLiveExecClientFactory)
    
    # Build the node
    try:
        node.build()
    except Exception as e:
        log(f"[NODE BUILD ERROR] {e}", "ERROR")
        return

    log(f"[READY] LIVE Trading {instrument} | Qty: {quantity} | Session: {session_id} | TraderID: {trader_id}")
    log(f"[WARNING] This is LIVE TRADING with real funds! Session: {session_id}", "WARNING")

    # Run node in background thread
    def run_node():
        try:
            node.run()
        except Exception as e:
            log(f"[NODE CRASH] {e}", "ERROR")
        finally:
            # Ensure cleanup
            try:
                node.stop()
                time.sleep(2)
                node.dispose()
            except:
                pass

    node_thread = threading.Thread(target=run_node, daemon=True, name=f"LiveNode-{user_id}-{session_id}")
    node_thread.start()

    log(f"[LIVE] Bot is running and connected to Binance LIVE (Session: {session_id})")

    last_status_check = time.time()
    error_count = 0
    max_errors = 5  # Fewer allowed errors for live
    health_check_failures = 0
    max_health_failures = 3
    consecutive_failures = 0
    max_consecutive_failures = 3

    try:
        while True:
            try:
                # Check if bot should still be active
                config = BotConfig.objects.only('is_active').get(user_id=user_id)
                if not config.is_active:
                    log(f"[STOP COMMAND RECEIVED] Graceful shutdown initiated... (Session: {session_id})", "WARNING")
                    break
                
                # Health check: verify node thread is alive
                if not node_thread.is_alive():
                    health_check_failures += 1
                    log(f"[HEALTH CHECK FAILED] Node thread not running (Failures: {health_check_failures}/{max_health_failures})", "ERROR")
                    if health_check_failures >= max_health_failures:
                        log(f"[CRITICAL] Too many health check failures, shutting down", "ERROR")
                        break
                else:
                    health_check_failures = 0  # Reset on success
                
                # Periodic status check
                current_time = time.time()
                if current_time - last_status_check > 60:  # Every minute for live
                    log(f"[STATUS] Live bot active - Instrument: {instrument} | Session: {session_id}", "DEBUG")
                    last_status_check = current_time
                
                # Reset error count on successful iteration
                error_count = 0
                consecutive_failures = 0
                
            except Exception as e:
                error_count += 1
                consecutive_failures += 1
                if error_count >= max_errors or consecutive_failures >= max_consecutive_failures:
                    log(f"[CRITICAL DB ERROR] {e} — Too many errors, forcing shutdown", "ERROR")
                    break
                log(f"[DB ERROR] {e} - Attempt {error_count}/{max_errors}", "WARNING")
                time.sleep(10)  # Longer sleep on error for live
                continue
            
            time.sleep(2)  # Longer sleep for live trading

    except KeyboardInterrupt:
        log(f"[INTERRUPT] Received keyboard interrupt, shutting down... (Session: {session_id})", "WARNING")
    except Exception as e:
        log(f"[UNEXPECTED ERROR] {e}", "ERROR")
    finally:
        log(f"[SHUTDOWN] Final cleanup for live bot session {session_id}...", "WARNING")
        
        # Stop the node
        try:
            node.stop()
            node_thread.join(timeout=30)  # Longer timeout for live
        except:
            pass
        
        # Dispose resources
        time.sleep(3)
        try:
            node.dispose()
        except Exception as e:
            log(f"[DISPOSE ERROR] {e}", "ERROR")

        # Update database status
        try:
            cfg = BotConfig.objects.get(user_id=user_id)
            cfg.is_active = False
            cfg.last_stopped = timezone.now()
            cfg.save(update_fields=['is_active', 'last_stopped', 'updated_at'])
            
            # Send notification (you could implement this)
            log(f"[NOTIFICATION] Live bot stopped. Please check logs. Session: {session_id}", "WARNING")
            
        except Exception as e:
            log(f"[STATUS UPDATE ERROR] {e}", "WARNING")

        log(f"[BOT STOPPED] Live trading bot session {session_id} fully terminated", "WARNING")

def start_live_bot(user_id: int, username: str, config_data: dict) -> bool:
    """Start a live bot in a separate thread with isolation"""
    with _process_lock:
        if user_id in _active_processes:
            thread = _active_processes[user_id]
            if thread.is_alive():
                print(f"Live bot already running for user {user_id}")
                return False
        
        # Create and start new thread with unique name
        thread_name = f"LiveBot-{user_id}-{int(time.time())}"
        thread = threading.Thread(
            target=_run_live_bot,
            args=(user_id, username, config_data),
            name=thread_name,
            daemon=True
        )
        
        thread.start()
        _active_processes[user_id] = thread
        print(f"Started LIVE bot for user {user_id} (Thread: {thread_name})")
        return True


def stop_live_bot(user_id: int) -> bool:
    """Stop a specific live bot"""
    with _process_lock:
        if user_id not in _active_processes:
            return False
        
        # Mark for shutdown through database
        import os
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
        django.setup()
        
        from ...models import BotConfig
        
        try:
            cfg = BotConfig.objects.get(user_id=user_id)
            cfg.is_active = False
            cfg.save(update_fields=['is_active'])
            
            # Wait for thread to finish
            thread = _active_processes[user_id]
            thread.join(timeout=30)
            
            del _active_processes[user_id]
            return True
        except Exception as e:
            print(f"Error stopping live bot: {e}")
            return False


def is_live_bot_running(user_id: int) -> bool:
    """Check if a live bot is running for the user"""
    with _process_lock:
        if user_id not in _active_processes:
            return False
        
        thread = _active_processes[user_id]
        return thread.is_alive()


# Setup signal handlers when module loads
_setup_signal_handlers()