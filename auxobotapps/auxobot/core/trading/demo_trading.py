import time
import multiprocessing
import threading
from decimal import Decimal
from typing import Dict
import signal
import sys
import hashlib
import os

from django.utils import timezone
from django.db.models import Q

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
DEFAULT_QUANTITY = Decimal('1.000')
MIN_QUANTITY = Decimal('0.001')  # More realistic minimum

# Global process tracking with better cleanup
_active_processes: Dict[int, multiprocessing.Process] = {}
_process_lock = threading.Lock()


def _setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down gracefully...")
        stop_all_bots()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def stop_all_bots():
    """Stop all running bots"""
    with _process_lock:
        for user_id, process in list(_active_processes.items()):
            if process.is_alive():
                print(f"Stopping bot for user {user_id}...")
                process.terminate()
                process.join(timeout=10)
        _active_processes.clear()

def _run_demo_bot(user_id: int, username: str, config_data: dict):
    """Main bot runner function - COMPLETELY ISOLATED PER USER"""
    import os
    import django
    
    # Setup Django with unique environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
    
    # Generate SHORTER unique session ID (6 chars max)
    session_id = hashlib.md5(f"DEMO_{user_id}_{username}_{time.time()}_{os.getpid()}".encode()).hexdigest()[:6]
    os.environ['USER_SESSION_ID'] = session_id
    
    django.setup()

    from ...models import DemoBotConfig, DemoTrade, DemoBotLog

    # Extract configuration
    instrument = config_data['instrument']
    custom_qty_str = config_data.get('custom_quantity')
    quantity = Decimal(custom_qty_str) if custom_qty_str else DEFAULT_QUANTITY
    quantity = max(quantity, MIN_QUANTITY)
    api_key = config_data['demo_api_key']
    api_secret = config_data['demo_api_secret']

    instrument_id_str = f"{instrument}-PERP.BINANCE"
    instrument_id = InstrumentId.from_str(instrument_id_str)

    def log(message: str, level: str = "INFO"):
        """Log message to database with user isolation"""
        try:
            DemoBotLog.objects.create(
                user_id=user_id,
                message=f"[{session_id}] {str(message).strip()[:950]}",
                level=level.upper()
            )
            # Cleanup old logs (keep last 500 per user)
            count = DemoBotLog.objects.filter(user_id=user_id).count()
            if count > 500:
                excess_ids = DemoBotLog.objects.filter(user_id=user_id)\
                    .order_by('timestamp')\
                    .values_list('id', flat=True)[:count - 500]
                DemoBotLog.objects.filter(id__in=list(excess_ids)).delete()
        except Exception as e:
            print(f"[{session_id}] LOG ERROR: {e} | {message}")

    log(f"[INIT] Initializing Nautilus node for {instrument}...")

    # Configure instrument provider
    instrument_provider_config = InstrumentProviderConfig(
        load_ids=(instrument_id_str,),
        load_all=False
    )

    # Configure trading node with SHORTER trader ID for Binance compatibility
    # MUST CONTAIN A HYPHEN! Format: DEMO-{user_id}-{session_id}
    trader_id = f"DEMO-{user_id}-{session_id}"
    if len(trader_id) > 20:  # Keep it reasonable
        trader_id = f"DEMO-{user_id}-{session_id[:4]}"
    
    node_config = TradingNodeConfig(
        trader_id=TraderId(trader_id),  # MUST contain hyphen!
        logging=LoggingConfig(
            log_level="INFO",
            log_colors=True,
            bypass_logging=False
        ),
        cache=CacheConfig(
            timestamps_as_iso8601=True,
            tick_capacity=50_000,
            bar_capacity=10_000
        ),
        message_bus=MessageBusConfig(),
        data_engine=LiveDataEngineConfig(),  # Simplified - no invalid parameters
        risk_engine=LiveRiskEngineConfig(
            max_order_submit_rate="100/00:00:01",
            max_order_modify_rate="100/00:00:01",
            bypass=False
        ),
        exec_engine=LiveExecEngineConfig(
            reconciliation=True,
            reconciliation_lookback_mins=60
        ),
        data_clients={
            "BINANCE": BinanceDataClientConfig(
                api_key=api_key,
                api_secret=api_secret,
                account_type=BinanceAccountType.USDT_FUTURES,
                testnet=True,
                instrument_provider=instrument_provider_config,
                use_agg_trade_ticks=True,
            )
        },
        exec_clients={
            "BINANCE": BinanceExecClientConfig(
                api_key=api_key,
                api_secret=api_secret,
                account_type=BinanceAccountType.USDT_FUTURES,
                testnet=True,
                instrument_provider=instrument_provider_config,
                use_gtd=False,
            )
        },
    )

    # Create and configure trading node
    node = TradingNode(config=node_config)

    # Configure strategy with user-specific settings
    strategy_config = GridStrategyConfig(
        instrument_id=instrument_id,
        user_id=user_id,  # Pass user_id for isolation
        grid_levels=GRID_LEVELS,
        order_quantity=quantity,
        grid_offset=float(GRID_OFFSET),
        grid_profit=1.2,
        recenter_drift_threshold=0.03,
        recenter_interval_seconds=300,
        breakout_threshold=0.06,
        trailing_stop_threshold=0.08,
        max_drawdown_percent=0.15,
        max_long_notional=Decimal("800"),
        max_short_notional=Decimal("800"),
        max_total_notional=Decimal("1200"),
        margin_safety_threshold=0.60,
        volatility_adapt_offset=True,
        enable_auto_resume=True,
        resume_cooldown_minutes=30,
        resume_price_tolerance=0.03,
        enable_breakout_stop=True,
        enable_exposure_limits=True,
        enable_margin_monitoring=True,
        enable_trailing_stop=True,
        enable_max_drawdown=True,
        stop_loss_percent=2.0,
        max_position_multiplier=3.0,
        trend_detection_period=20,
        asymmetric_profit_factor=1.5,
        consider_funding_rate=True,
        dynamic_grid_adjustment=True,
        min_grid_levels=5,
        max_grid_levels=30,
        order_validation_distance=0.001,
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

    log(f"[READY] Trading {instrument} | Qty: {quantity} | Session: {session_id} | TraderID: {trader_id}")

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

    node_thread = threading.Thread(target=run_node, daemon=True, name=f"Node-{user_id}-{session_id}")
    node_thread.start()

    log(f"[LIVE] Bot is running and connected to Binance Testnet (Session: {session_id})")

    last_fill_ts = timezone.now() - timezone.timedelta(days=1)
    last_status_check = time.time()
    error_count = 0
    max_errors = 10
    health_check_failures = 0
    max_health_failures = 5

    try:
        while True:
            try:
                # Check if bot should still be active
                config = DemoBotConfig.objects.only('is_active').get(user_id=user_id)
                if not config.is_active:
                    log(f"[STOP COMMAND RECEIVED] Graceful shutdown initiated... (Session: {session_id})")
                    break
                
                # Health check: verify node thread is alive
                if not node_thread.is_alive():
                    health_check_failures += 1
                    log(f"[HEALTH CHECK FAILED] Node thread not running (Failures: {health_check_failures}/{max_health_failures})", "WARNING")
                    if health_check_failures >= max_health_failures:
                        log(f"[CRITICAL] Too many health check failures, shutting down", "ERROR")
                        break
                else:
                    health_check_failures = 0  # Reset on success
                
                # Periodic status check
                if time.time() - last_status_check > 30:
                    log(f"[STATUS] Bot active - Instrument: {instrument} | Session: {session_id}", "DEBUG")
                    last_status_check = time.time()
                
                # Process fills from database (optional)
                # Reset error count on successful iteration
                error_count = 0
                
            except Exception as e:
                error_count += 1
                if error_count >= max_errors:
                    log(f"[CRITICAL DB ERROR] {e} — Too many errors, forcing shutdown", "ERROR")
                    break
                log(f"[DB ERROR] {e} - Attempt {error_count}/{max_errors}", "WARNING")
                time.sleep(5)
                continue
            
            time.sleep(1)  # Main loop sleep

    except KeyboardInterrupt:
        log(f"[INTERRUPT] Received keyboard interrupt, shutting down... (Session: {session_id})")
    except Exception as e:
        log(f"[UNEXPECTED ERROR] {e}", "ERROR")
    finally:
        log(f"[SHUTDOWN] Final cleanup for session {session_id}...")
        
        # Stop the node
        try:
            node.stop()
            node_thread.join(timeout=15)
        except:
            pass
        
        # Dispose resources
        time.sleep(2)
        try:
            node.dispose()
        except Exception as e:
            log(f"[DISPOSE ERROR] {e}", "ERROR")

        # Update database status
        try:
            cfg = DemoBotConfig.objects.get(user_id=user_id)
            cfg.is_active = False
            cfg.last_stopped = timezone.now()
            cfg.save(update_fields=['is_active', 'last_stopped', 'updated_at'])
        except Exception as e:
            log(f"[STATUS UPDATE ERROR] {e}", "WARNING")

        log(f"[BOT STOPPED] Session {session_id} fully terminated")

def start_demo_bot(user_id: int, username: str, config_data: dict) -> bool:
    """Start a demo bot in a separate process with isolation"""
    with _process_lock:
        if user_id in _active_processes:
            process = _active_processes[user_id]
            if process.is_alive():
                print(f"Bot already running for user {user_id}")
                return False
        
        # Create and start new process with isolated environment
        process = multiprocessing.Process(
            target=_run_demo_bot,
            args=(user_id, username, config_data),
            name=f"DemoBot-{user_id}-{int(time.time())}",
            daemon=True
        )
        
        process.start()
        _active_processes[user_id] = process
        print(f"Started demo bot for user {user_id} (PID: {process.pid})")
        return True


def stop_demo_bot(user_id: int) -> bool:
    """Stop a specific demo bot"""
    with _process_lock:
        if user_id not in _active_processes:
            return False
        
        process = _active_processes[user_id]
        if process.is_alive():
            process.terminate()
            process.join(timeout=10)
        
        del _active_processes[user_id]
        return True


def is_bot_running(user_id: int) -> bool:
    """Check if a bot is running for the user"""
    with _process_lock:
        if user_id not in _active_processes:
            return False
        
        process = _active_processes[user_id]
        return process.is_alive()


# Setup signal handlers when module loads
_setup_signal_handlers()