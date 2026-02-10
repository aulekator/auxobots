from decimal import Decimal
import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from collections import deque

from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import QuoteTick, TradeTick, Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId, Venue
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.currencies import USDT
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model.orders import Order
from nautilus_trader.model.enums import PositionSide
from nautilus_trader.model.orders.market import MarketOrder


@dataclass
class GridTrade:
    """Simple data structure for tracking grid trades"""
    trade_id: str
    entry_order_id: str
    entry_price: Decimal
    tp_order_id: Optional[str] = None
    sl_order_id: Optional[str] = None
    grid_level: Optional[int] = None
    entry_side: Optional[OrderSide] = None
    entry_time: float = 0.0
    profit_pct: float = 0.0
    closed: bool = False


class SimpleMovingAverage:
    """Simple moving average indicator"""
    def __init__(self, period: int):
        self.period = period
        self.prices = deque(maxlen=period)
        self.value: Optional[Decimal] = None
        self.initialized = False
    
    def update(self, price: Decimal) -> None:
        self.prices.append(price)
        if len(self.prices) == self.period:
            self.value = sum(self.prices) / Decimal(self.period)
            self.initialized = True


class GridStrategyConfig(StrategyConfig):
    instrument_id: InstrumentId
    user_id: int = None 
    grid_levels: int = 15
    order_quantity: Decimal = Decimal("1.000")
    grid_offset: float = 0.08
    grid_profit: float = 1.2
    recenter_drift_threshold: float = 0.03
    recenter_interval_seconds: int = 300

    breakout_threshold: float = 0.06
    trailing_stop_threshold: float = 0.08
    max_drawdown_percent: float = 0.15
    max_long_notional: Decimal = Decimal("800")
    max_short_notional: Decimal = Decimal("800")
    max_total_notional: Decimal = Decimal("1200")
    margin_safety_threshold: float = 0.60
    volatility_adapt_offset: bool = True
    enable_auto_resume: bool = True
    resume_cooldown_minutes: int = 30
    resume_price_tolerance: float = 0.03

    enable_breakout_stop: bool = True
    enable_exposure_limits: bool = True
    enable_margin_monitoring: bool = True
    enable_trailing_stop: bool = True
    enable_max_drawdown: bool = True


    stop_loss_percent: float = 2.0  # 2% stop loss
    max_position_multiplier: float = 3.0  # Max 3x grid size
    trend_detection_period: int = 20  # Period for trend detection
    asymmetric_profit_factor: float = 1.5  # Higher profit on trend side
    consider_funding_rate: bool = True  # Consider funding rates
    dynamic_grid_adjustment: bool = True  # Enable dynamic grid adjustment
    min_grid_levels: int = 5  # Minimum grid levels
    max_grid_levels: int = 30  # Maximum grid levels
    order_validation_distance: float = 0.001  # 0.1% minimum from market price


class GridStrategy(Strategy):
    def __init__(self, config: GridStrategyConfig) -> None:
        super().__init__(config)

        # Simplified tracking - use Nautilus cache instead
        self.grid_trades: Dict[str, GridTrade] = {}
        self.grid_order_ids: set = set()  # Track active grid order IDs
        self.tp_sl_order_ids: set = set()  # Track TP/SL order IDs
        
        self.instrument_id = config.instrument_id
        self.instrument: Optional[Instrument] = None
        self.user_prefix = f"USER_{config.user_id}_" if config.user_id else ""

        self.active_trade = None
        self.active_tp_order_id = None
        self.active_sl_order_id = None
        self.position_entry_price = None

        # Configuration parameters
        self.grid_levels = config.grid_levels
        self.order_quantity = config.order_quantity
        self.base_grid_offset = Decimal(str(config.grid_offset))
        self.grid_profit = Decimal(str(config.grid_profit))
        self.recenter_drift = Decimal(str(config.recenter_drift_threshold))
        self.recenter_interval = config.recenter_interval_seconds

        # Risk parameters
        self.breakout_threshold = Decimal(str(config.breakout_threshold))
        self.trailing_stop_threshold = Decimal(str(config.trailing_stop_threshold))
        self.max_drawdown_percent = Decimal(str(config.max_drawdown_percent))
        self.max_long_notional = config.max_long_notional
        self.max_short_notional = config.max_short_notional
        self.max_total_notional = config.max_total_notional
        self.margin_safety_threshold = Decimal(str(config.margin_safety_threshold))
        self.vol_adapt = config.volatility_adapt_offset
        self.enable_auto_resume = config.enable_auto_resume
        self.resume_cooldown = config.resume_cooldown_minutes * 60
        self.resume_tolerance = Decimal(str(config.resume_price_tolerance))

        # Feature toggles
        self.enable_breakout_stop = config.enable_breakout_stop
        self.enable_exposure_limits = config.enable_exposure_limits
        self.enable_margin_monitoring = config.enable_margin_monitoring
        self.enable_trailing_stop = config.enable_trailing_stop
        self.enable_max_drawdown = config.enable_max_drawdown
        self.dynamic_grid_adjustment = config.dynamic_grid_adjustment
        self.order_validation_distance = Decimal(str(config.order_validation_distance))

        self.grid_levels_by_order_id: Dict[str, int] = {}

        # State variables
        self.current_mid_price: Optional[Decimal] = None
        self.lower_price: Optional[Decimal] = None
        self.upper_price: Optional[Decimal] = None
        self.original_lower: Optional[Decimal] = None
        self.original_upper: Optional[Decimal] = None
        self.highest_mid_since_start: Decimal = Decimal("0")
        self.last_recenter_time: float = 0.0
        self.last_pause_time: float = 0.0
        self.grid_active = False
        self.paused_due_to_risk = False
        self.last_margin_check_time: float = 0.0
        self.starting_equity: Optional[Money] = None
        self.effective_grid_levels: int = config.grid_levels

        # Technical indicators
        self.atr_period = 14
        self.atr_values = deque(maxlen=self.atr_period)
        self.prev_close: Optional[Decimal] = None
        
        # Simple trend detection
        self.sma_fast = SimpleMovingAverage(period=9)
        self.sma_slow = SimpleMovingAverage(period=21)
        self.volatility_values = deque(maxlen=20)
        self.price_history = deque(maxlen=50)  # For basic trend calculation

        # Enhanced parameters
        self.stop_loss_percent = Decimal(str(config.stop_loss_percent)) / Decimal("100")
        self.max_position_multiplier = Decimal(str(config.max_position_multiplier))
        self.asymmetric_profit_factor = Decimal(str(config.asymmetric_profit_factor))
        self.consider_funding_rate = config.consider_funding_rate
        self.min_grid_levels = config.min_grid_levels
        self.max_grid_levels = config.max_grid_levels
        
        # Trend detection
        self.trend_strength = 0
        self.is_uptrend = False
        self.is_downtrend = False
        
        # Funding rate tracking
        self.last_funding_rate = Decimal("0")
        self.funding_rate_accumulated = Decimal("0")
        
        # Performance metrics
        self.performance_tracker = PerformanceTracker()
        
        # Position tracking (simplified)
        self.max_grid_position = self.order_quantity * Decimal(str(self.grid_levels))
        self.max_allowed_position = self.max_grid_position * self.max_position_multiplier

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.instrument_id)
        if not self.instrument:
            self.log.error(f"Instrument not found: {self.instrument_id}")
            self.stop()
            return

        bar_type = BarType.from_str(f"{self.instrument_id}-15-MINUTE-LAST-EXTERNAL")
        self.subscribe_bars(bar_type)
        self.subscribe_quote_ticks(self.instrument_id)
        self.subscribe_trade_ticks(self.instrument_id)

        self.log.info(f"Enhanced GridStrategy started for {self.instrument_id}")

    def on_bar(self, bar: Bar) -> None:
        """Handle bar data for indicators"""
        if self.prev_close is None:
            self.prev_close = bar.close
            return

        # Calculate True Range for ATR
        tr = max(
            bar.high - bar.low,
            abs(bar.high - self.prev_close),
            abs(bar.low - self.prev_close)
        )
        self.atr_values.append(tr)
        self.prev_close = bar.close
        
        # Update price history for trend calculation
        self.price_history.append(bar.close)
        
        # Update SMA indicators
        self.sma_fast.update(bar.close)
        self.sma_slow.update(bar.close)
        
        # Calculate volatility
        if len(self.volatility_values) > 0:
            volatility = abs((bar.close - bar.open) / bar.open)
            self.volatility_values.append(volatility)
        else:
            self.volatility_values.append(Decimal("0.01"))  # Default 1% volatility
        
        # Detect trend and adjust grid
        self._detect_trend()
        
        # Dynamic grid adjustment
        if self.dynamic_grid_adjustment:
            self._calculate_dynamic_grid_levels()

    def _detect_trend(self) -> None:
        """Simple trend detection using price action and SMAs"""
        if len(self.price_history) < 20:
            return
        
        # Calculate simple trend based on recent price action
        recent_prices = list(self.price_history)
        if len(recent_prices) < 10:
            return
        
        # Calculate price slope
        oldest_price = recent_prices[0]
        newest_price = recent_prices[-1]
        price_change_pct = (newest_price - oldest_price) / oldest_price
        
        # Use SMA cross for trend direction
        if self.sma_fast.initialized and self.sma_slow.initialized:
            if self.sma_fast.value > self.sma_slow.value:
                self.is_uptrend = True
                self.is_downtrend = False
            else:
                self.is_uptrend = False
                self.is_downtrend = True
        
        # Calculate trend strength based on price change magnitude
        self.trend_strength = abs(float(price_change_pct)) * 100  # Convert to percentage
        
        # Log trend information
        if self.trend_strength > 3:  # Strong trend if > 3%
            if self.is_uptrend:
                self.log.debug(f"Strong uptrend detected (Strength: {self.trend_strength:.1f}%)")
            else:
                self.log.debug(f"Strong downtrend detected (Strength: {self.trend_strength:.1f}%)")

    def _calculate_dynamic_grid_levels(self) -> None:
        """Dynamically adjust grid levels based on market conditions"""
        if not self.current_mid_price or len(self.volatility_values) < 5:
            return
        
        avg_volatility = sum(self.volatility_values) / len(self.volatility_values)
        base_levels = self.grid_levels
        
        # Adjust based on volatility
        if avg_volatility > Decimal("0.03"):  # High volatility (>3%)
            # Reduce grid levels in high volatility
            adjustment = max(0.5, 1.0 - (avg_volatility / Decimal("0.05")))
            adjusted = int(base_levels * adjustment)
        elif avg_volatility < Decimal("0.01"):  # Low volatility (<1%)
            # Increase grid levels in low volatility
            adjustment = min(1.5, 1.0 + (Decimal("0.01") / avg_volatility))
            adjusted = int(base_levels * adjustment)
        else:
            adjusted = base_levels
        
        # Adjust based on trend strength
        if self.trend_strength > 4:  # Strong trend
            adjusted = max(self.min_grid_levels, adjusted // 2)
        elif self.trend_strength > 2:  # Moderate trend
            adjusted = max(self.min_grid_levels, int(adjusted * 2 // 3))
        
        # Apply limits
        self.effective_grid_levels = max(self.min_grid_levels, 
                                        min(self.max_grid_levels, adjusted))
        
        if self.effective_grid_levels != self.grid_levels:
            self.log.info(f"Dynamic grid adjustment: {self.grid_levels} -> {self.effective_grid_levels} "
                         f"(Vol: {avg_volatility*100:.1f}%, Trend: {self.trend_strength:.1f}%)")

    def _check_position_size(self) -> bool:
        """Check if position exceeds maximum allowed size"""
        position = self.cache.position_for_instrument(self.instrument_id)
        if not position:
            return True
        
        current_qty = abs(float(position.quantity))
        max_allowed = float(self.max_allowed_position)
        
        if current_qty > max_allowed:
            self.log.warning(f"Position size {current_qty} exceeds maximum {max_allowed}")
            return False
        
        # Check based on grid trades instead of active_trades dict
        active_trade_count = sum(1 for t in self.grid_trades.values() if not t.closed)
        if active_trade_count > self.effective_grid_levels * 2:  # Allow 2x for TP/SL orders
            self.log.warning(f"Too many active trades: {active_trade_count}")
            return False
        
        return True
        
    def _get_atr_multiplier(self) -> Decimal:
        """Calculate ATR-based volatility multiplier"""
        if not self.atr_values or not self.current_mid_price:
            return Decimal("1")
        
        if len(self.atr_values) < 5:  # Need minimum data
            return Decimal("1")
        
        current_atr = sum(self.atr_values) / len(self.atr_values)
        atr_percent = current_atr / float(self.current_mid_price)
        
        # Normalize to reasonable range (0.7 to 1.8)
        return min(max(Decimal(str(atr_percent / 0.01)), Decimal("0.7")), Decimal("1.8"))
    
    def _handle_position_close(self, reason: str):
        """Handle position closure and reset grid"""
        # Clear active trade tracking
        self.active_trade = None
        self.active_tp_order_id = None
        self.active_sl_order_id = None
        
        # Cancel any remaining TP/SL orders
        for order_id in [self.active_tp_order_id, self.active_sl_order_id]:
            if order_id:
                order = self.cache.order(order_id)
                if order and order.is_open:
                    self.cancel_order(order)
        
        # Wait a moment for position to settle
        time.sleep(1)
        
        # Re-center grid at current price
        if self.current_mid_price:
            self._center_grid(self.current_mid_price)
        
        self.log.info(f"Position closed ({reason}), grid reset")

    def on_quote_tick(self, tick: QuoteTick) -> None:
        mid = (tick.bid_price + tick.ask_price) / Decimal("2")
        self._process_price_update(mid)

    def on_trade_tick(self, tick: TradeTick) -> None:
        if self.current_mid_price is None:
            self._process_price_update(Decimal(str(tick.price.as_double())))

    def _get_current_position_notional(self) -> Tuple[Decimal, Decimal]:
        """Calculate current position notional values"""
        if not self.current_mid_price:
            return Decimal("0"), Decimal("0")

        long_n = short_n = Decimal("0")
        for position in self.cache.positions(instrument_id=self.instrument_id):
            if position.is_closed:
                continue
            
            # Calculate notional value
            quantity = abs(float(position.quantity))
            notional = Decimal(str(quantity * float(self.current_mid_price)))
            
            if position.side == PositionSide.LONG:
                long_n += notional
            elif position.side == PositionSide.SHORT:
                short_n += notional
        
        return long_n, short_n

    def _check_exposure_limits(self) -> bool:
        """Check if exposure limits are breached"""
        if not self.enable_exposure_limits or not self.grid_active:
            return True
        
        long_n, short_n = self._get_current_position_notional()
        total_n = long_n + short_n
        
        if (long_n > self.max_long_notional or 
            short_n > self.max_short_notional or 
            total_n > self.max_total_notional):
            
            self.log.error(f"Exposure breach: Long={long_n}, Short={short_n}, Total={total_n}")
            return False
        
        return True
    
    def _check_drawdown(self) -> bool:
        """Check if maximum drawdown is breached"""
        if not self.enable_max_drawdown or not self.starting_equity:
            return True
        
        account = self.cache.account_for_venue(Venue("BINANCE"))
        if not account:
            return True
        
        try:
            current_usdt = account.balance(currency=USDT)
            if current_usdt:
                current_total = current_usdt.total.as_decimal()
                threshold = self.starting_equity.as_decimal() * (Decimal("1") - self.max_drawdown_percent)
                
                if current_total < threshold:
                    self.log.error(f"Max drawdown breached: {current_total} < {threshold}")
                    return False
        except Exception as e:
            self.log.warning(f"Drawdown check error: {e}")
        
        return True

    def _flatten_and_pause(self, reason: str) -> None:
        """Flatten all positions and pause the grid"""
        if self.paused_due_to_risk:
            return
        
        self.log.warning(f"SAFETY TRIGGER: {reason} → Flattening + pausing")
        
        # Cancel all active orders
        self.cancel_all_orders(self.instrument_id)
        
        # Clear all order tracking
        self.grid_order_ids.clear()
        self.tp_sl_order_ids.clear()
        self.grid_levels_by_order_id.clear()
        
        # Close all positions
        self.close_all_positions(self.instrument_id)
        
        # Mark all trades as closed
        for trade in self.grid_trades.values():
            trade.closed = True
        
        # Update state
        self.grid_active = False
        self.paused_due_to_risk = True
        self.last_pause_time = time.time()
        
    def _process_price_update(self, mid_price: Decimal) -> None:
        """Process price updates and trigger appropriate actions"""
        if self.current_mid_price is None:
            self._center_grid(mid_price)
            return

        self.current_mid_price = mid_price
        if self.highest_mid_since_start < mid_price:
            self.highest_mid_since_start = mid_price

        # Check for auto-resume
        if self.paused_due_to_risk and self.enable_auto_resume:
            if self._should_resume_grid(mid_price):
                self.log.info("Auto-resuming grid after cooldown + price sanity")
                self.paused_due_to_risk = False
                self._center_grid(mid_price)
                return

        if self.paused_due_to_risk:
            return

        # Check breakout stop
        if self.enable_breakout_stop and self.grid_active and self.lower_price and self.upper_price:
            if self._check_breakout(mid_price):
                self._flatten_and_pause(f"Breakout ±{self.breakout_threshold:.0%}")
                return

        # Check exposure limits
        if not self._check_exposure_limits():
            self._flatten_and_pause("Exposure limits")
            return

        # Check drawdown
        if not self._check_drawdown():
            self._flatten_and_pause("Max drawdown")
            return

        # Check trailing stop
        if self.enable_trailing_stop and self.grid_active:
            if self._check_trailing_stop(mid_price):
                self._flatten_and_pause(f"Trailing stop {self.trailing_stop_threshold:.0%} from high")
                return

        # Check for recentering
        now = time.time()
        if now - self.last_recenter_time > self.recenter_interval:
            drift = abs(mid_price - self.current_mid_price) / self.current_mid_price
            if drift > self.recenter_drift:
                self.log.info(f"Drift {drift:.1%} → Re-centering")
                self.cancel_all_orders(self.instrument_id)
                self.grid_order_ids.clear()
                self._center_grid(mid_price)
                self.last_recenter_time = now

    def _should_resume_grid(self, mid_price: Decimal) -> bool:
        """Check if grid should be resumed"""
        if time.time() - self.last_pause_time < self.resume_cooldown:
            return False
        
        if not self.original_lower or not self.original_upper:
            return False
        
        return (mid_price > self.original_lower * (Decimal("1") - self.resume_tolerance) and
                mid_price < self.original_upper * (Decimal("1") + self.resume_tolerance))

    def _check_breakout(self, mid_price: Decimal) -> bool:
        """Check if price has broken out of grid range"""
        lower_bound = self.lower_price * (Decimal("1") - self.breakout_threshold)
        upper_bound = self.upper_price * (Decimal("1") + self.breakout_threshold)
        return mid_price < lower_bound or mid_price > upper_bound

    def _check_trailing_stop(self, mid_price: Decimal) -> bool:
        """Check if trailing stop should trigger"""
        trail_low = self.highest_mid_since_start * (Decimal("1") - self.trailing_stop_threshold)
        return mid_price < trail_low

    def _center_grid(self, mid_price: Decimal) -> None:
        """Center the grid around the current price"""
        self.current_mid_price = mid_price
        if self.highest_mid_since_start < mid_price:
            self.highest_mid_since_start = mid_price

        # Calculate offset with ATR adjustment
        offset = self.base_grid_offset
        if self.vol_adapt:
            offset *= self._get_atr_multiplier()

        half = offset / Decimal("2")
        self.lower_price = mid_price * (Decimal("1") - half)
        self.upper_price = mid_price * (Decimal("1") + half)
        
        if self.original_lower is None:
            self.original_lower = self.lower_price
            self.original_upper = self.upper_price

        # Set starting equity if not set
        if self.starting_equity is None:
            account = self.cache.account_for_venue(Venue("BINANCE"))
            if account:
                try:
                    usdt_balance = account.balance(currency=USDT)
                    if usdt_balance and usdt_balance.total > Money(0, USDT):
                        self.starting_equity = usdt_balance.total
                        self.log.info(f"Starting equity set to {self.starting_equity}")
                except Exception as e:
                    self.log.error(f"Failed to get USDT balance: {e}")

        # Clear previous grid tracking
        self.grid_order_ids.clear()
        self.grid_levels_by_order_id.clear()
        
        self.log.info(
            f"Grid centered at {mid_price:.{self.instrument.price_precision}f} | "
            f"Range: {self.lower_price:.{self.instrument.price_precision}f} – {self.upper_price:.{self.instrument.price_precision}f} "
            f"(±{half * 100:.2f}%{' - adapted by ATR' if self.vol_adapt else ''})"
        )

        self._place_grid_orders()
        self.grid_active = True
        self.paused_due_to_risk = False
        
    def _make_price(self, raw_price: float) -> Price:
        """Create Price object with proper precision"""
        return Price(self.instrument.make_price(raw_price), self.instrument.price_precision)
    
    def _make_quantity(self) -> Quantity:
        """Create Quantity object with proper precision and validation"""
        # Use Decimal directly
        raw_qty = self.order_quantity
        precision = self.instrument.size_precision
        
        # Create quantity directly from Decimal
        qty = Quantity(
            value=float(raw_qty),
            precision=precision,
        )
        
        # Enforce minimum quantity
        if qty < self.instrument.min_quantity:
            self.log.warning(
                f"Quantity {qty} below instrument min {self.instrument.min_quantity}. "
                f"Adjusting upward."
            )
            qty = self.instrument.min_quantity
        
        return qty

    def _is_price_valid(self, price: Price, is_buy: bool) -> bool:
        """Validate that price is not too close to current market"""
        if not self.current_mid_price:
            return True
        
        distance_pct = abs(float(price) - float(self.current_mid_price)) / float(self.current_mid_price)
        
        # Different validation for buy vs sell
        if is_buy:
            # Buy orders should be below current price
            if float(price) >= float(self.current_mid_price):
                return False
        else:
            # Sell orders should be above current price
            if float(price) <= float(self.current_mid_price):
                return False
        
        # Minimum distance check
        return distance_pct >= float(self.order_validation_distance)

    def _place_grid_orders(self) -> None:
        """Place all grid orders"""
        qty = self._make_quantity()
        
        # Calculate geometric ratio
        ratio = (self.upper_price / self.lower_price) ** (Decimal("1") / Decimal(str(self.effective_grid_levels * 2)))
        
        # Clear previous grid orders tracking
        self.grid_order_ids.clear()
        
        # Dictionary to track grid level for each order
        grid_levels_by_order_id = {}
        
        orders_placed = 0
        for i in range(1, self.effective_grid_levels + 1):
            # Buy order
            buy_price_raw = float(self.current_mid_price * (ratio ** -Decimal(str(i))))
            buy_price = self._make_price(buy_price_raw)
            
            # Validate buy price
            if self._is_price_valid(buy_price, is_buy=True):
                buy_order = self.order_factory.limit(
                    instrument_id=self.instrument_id,
                    order_side=OrderSide.BUY,
                    price=buy_price,
                    quantity=qty,
                    post_only=True,
                    time_in_force=TimeInForce.GTC,
                    reduce_only=False,  # Grid orders should NOT be reduce-only
                )
                self.submit_order(buy_order)
                self.grid_order_ids.add(buy_order.client_order_id)
                # Store grid level separately
                grid_levels_by_order_id[buy_order.client_order_id] = i
                orders_placed += 1
            else:
                self.log.warning(f"Skipping buy order at {buy_price} - too close to market")
            
            # Sell order
            sell_price_raw = float(self.current_mid_price * (ratio ** Decimal(str(i))))
            sell_price = self._make_price(sell_price_raw)
            
            # Validate sell price
            if self._is_price_valid(sell_price, is_buy=False):
                sell_order = self.order_factory.limit(
                    instrument_id=self.instrument_id,
                    order_side=OrderSide.SELL,
                    price=sell_price,
                    quantity=qty,
                    post_only=True,
                    time_in_force=TimeInForce.GTC,
                    reduce_only=False,  # Grid orders should NOT be reduce-only
                )
                self.submit_order(sell_order)
                self.grid_order_ids.add(sell_order.client_order_id)
                # Store grid level separately
                grid_levels_by_order_id[sell_order.client_order_id] = i
                orders_placed += 1
            else:
                self.log.warning(f"Skipping sell order at {sell_price} - too close to market")
        
        # Store grid levels mapping
        self.grid_levels_by_order_id = grid_levels_by_order_id
        
        self.log.info(f"Placed {orders_placed} geometric grid orders (effective levels: {self.effective_grid_levels}, trend strength: {self.trend_strength:.1f}%)")
            
    def on_fill(self, fill) -> None:
        """Handle order fills with proper TP/SL management"""
        self.log.info(f"[FILL DETECTED] {fill.order.side} at {fill.order.price}")
        
        if not self.grid_active or self.paused_due_to_risk:
            return
        
        # Remove from grid order tracking
        if fill.order.client_order_id in self.grid_order_ids:
            self.grid_order_ids.discard(fill.order.client_order_id)
            self.log.info(f"Removed {fill.order.client_order_id} from grid orders")
        
        # Get current position AFTER fill
        position = self.cache.position_for_instrument(self.instrument_id)
        self.log.info(f"Current position after fill: {position}")
        
        # Check if we already have TP/SL for this position
        if self.active_tp_order_id or self.active_sl_order_id:
            self.log.info("TP/SL already active, not placing new ones")
            return
        
        # Place TP/SL for the position
        entry_price = Decimal(str(fill.order.price.as_double()))
        quantity = self._make_quantity()
        
        # If position exists, use its quantity
        if position and not position.is_closed:
            quantity = abs(position.quantity)
            self.log.info(f"Using position quantity: {quantity}")
        
        # Place TP/SL orders
        tp_order, sl_order = self._place_position_tp_sl(
            entry_price=entry_price,
            side=fill.order.side,
            quantity=quantity
        )
        
        if tp_order and sl_order:
            # Track this as the active trade
            self.active_trade = {
                'entry_order_id': fill.order.client_order_id,
                'entry_price': entry_price,
                'entry_side': fill.order.side,
                'tp_order_id': tp_order.client_order_id,
                'sl_order_id': sl_order.client_order_id,
                'quantity': float(quantity),
                'entry_time': time.time()
            }
            
            # Cancel all other grid orders (single position mode)
            self._cancel_all_grid_orders()
            
    def _place_position_tp_sl(self, entry_price: Decimal, side: OrderSide, quantity: Quantity):
        """Place proper TP/SL orders for a position"""
        try:
            # Calculate TP price (grid_profit% from entry)
            if side == OrderSide.BUY:
                tp_price_raw = float(entry_price * (Decimal("1") + self.grid_profit / Decimal("100")))
                sl_price_raw = float(entry_price * (Decimal("1") - self.stop_loss_percent))
                tp_side = OrderSide.SELL
                sl_side = OrderSide.SELL
            else:  # SELL
                tp_price_raw = float(entry_price * (Decimal("1") - self.grid_profit / Decimal("100")))
                sl_price_raw = float(entry_price * (Decimal("1") + self.stop_loss_percent))
                tp_side = OrderSide.BUY
                sl_side = OrderSide.BUY
            
            tp_price = self._make_price(tp_price_raw)
            sl_price = self._make_price(sl_price_raw)
            
            self.log.info(f"Placing TP/SL for {side} position:")
            self.log.info(f"  Entry: {entry_price:.4f}")
            self.log.info(f"  TP: {tp_price} ({self.grid_profit:.1f}%)")
            self.log.info(f"  SL: {sl_price} ({self.stop_loss_percent*100:.1f}%)")
            
            # Place TAKE-PROFIT order (LIMIT)
            tp_order = self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=tp_side,
                price=tp_price,
                quantity=quantity,
                time_in_force=TimeInForce.GTC,
                post_only=True,
                reduce_only=True,  # CRITICAL for futures
            )
            
            # Place STOP-LOSS order (STOP-MARKET)
            sl_order = self.order_factory.stop_market(
                instrument_id=self.instrument_id,
                order_side=sl_side,
                quantity=quantity,
                trigger_price=sl_price,
                time_in_force=TimeInForce.GTC,
                reduce_only=True,  # CRITICAL for futures
            )
            
            # Submit orders
            self.submit_order(tp_order)
            self.submit_order(sl_order)
            
            # Store TP/SL order IDs
            self.active_tp_order_id = tp_order.client_order_id
            self.active_sl_order_id = sl_order.client_order_id
            
            self.log.info(f"TP Order: {tp_order.client_order_id}")
            self.log.info(f"SL Order: {sl_order.client_order_id}")
            
            return tp_order, sl_order
            
        except Exception as e:
            self.log.error(f"Error placing TP/SL: {e}")
            return None, None
                    
    def _calculate_profit_percentage(self, side: OrderSide) -> Decimal:
        """Calculate profit percentage based on trend direction"""
        base_profit = self.grid_profit
        
        if self.is_uptrend and side == OrderSide.BUY:
            # Higher profit on buys during uptrend
            return base_profit * self.asymmetric_profit_factor
        elif self.is_downtrend and side == OrderSide.SELL:
            # Higher profit on sells during downtrend
            return base_profit * self.asymmetric_profit_factor
        else:
            # Normal profit for counter-trend trades
            return base_profit

    def _place_buy_trade_orders(self, trade: GridTrade, qty: Quantity) -> None:
        """Place TP and SL orders for a buy trade"""
        # Calculate take-profit price
        profit_pct = Decimal(str(trade.profit_pct))
        target_raw = float(trade.entry_price * (Decimal("1") + profit_pct / Decimal("100")))
        target_price = self._make_price(target_raw)
        
        # Calculate stop-loss price
        stop_loss_raw = float(trade.entry_price * (Decimal("1") - self.stop_loss_percent))
        stop_loss_price = self._make_price(stop_loss_raw)
        
        # Place take-profit order
        tp_order = self.order_factory.limit(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            price=target_price,
            quantity=qty,
            post_only=True,
            time_in_force=TimeInForce.GTC,
            reduce_only=True,
        )
        
        # Place stop-loss order (FIXED: no price parameter for stop-market)
        sl_order = self.order_factory.stop_market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=qty,
            trigger_price=stop_loss_price,  # Only trigger_price, no price parameter
            time_in_force=TimeInForce.GTC,
            reduce_only=True,
        )
        
        # Store order IDs
        trade.tp_order_id = tp_order.client_order_id
        trade.sl_order_id = sl_order.client_order_id
        
        # Track TP/SL orders
        self.tp_sl_order_ids.add(tp_order.client_order_id)
        self.tp_sl_order_ids.add(sl_order.client_order_id)
        
        # Submit orders
        self.submit_order(tp_order)
        self.submit_order(sl_order)
        
        self.log.info(f"Trade {trade.trade_id}: BUY at {trade.entry_price}, "
                     f"TP at {target_price} ({profit_pct:.1f}%), "
                     f"SL at {stop_loss_price} ({self.stop_loss_percent*100:.1f}%)")

    def _place_sell_trade_orders(self, trade: GridTrade, qty: Quantity) -> None:
        """Place TP and SL orders for a sell trade"""
        # Calculate take-profit price
        profit_pct = Decimal(str(trade.profit_pct))
        target_raw = float(trade.entry_price * (Decimal("1") - profit_pct / Decimal("100")))
        target_price = self._make_price(target_raw)
        
        # Calculate stop-loss price
        stop_loss_raw = float(trade.entry_price * (Decimal("1") + self.stop_loss_percent))
        stop_loss_price = self._make_price(stop_loss_raw)
        
        # Place take-profit order
        tp_order = self.order_factory.limit(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            price=target_price,
            quantity=qty,
            post_only=True,
            time_in_force=TimeInForce.GTC,
            reduce_only=True,
        )
        
        # Place stop-loss order (FIXED: no price parameter for stop-market)
        sl_order = self.order_factory.stop_market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=qty,
            trigger_price=stop_loss_price,  # Only trigger_price, no price parameter
            time_in_force=TimeInForce.GTC,
            reduce_only=True,
        )
        
        # Store order IDs
        trade.tp_order_id = tp_order.client_order_id
        trade.sl_order_id = sl_order.client_order_id
        
        # Track TP/SL orders
        self.tp_sl_order_ids.add(tp_order.client_order_id)
        self.tp_sl_order_ids.add(sl_order.client_order_id)
        
        # Submit orders
        self.submit_order(tp_order)
        self.submit_order(sl_order)
        
        self.log.info(f"Trade {trade.trade_id}: SELL at {trade.entry_price}, "
                     f"TP at {target_price} ({profit_pct:.1f}%), "
                     f"SL at {stop_loss_price} ({self.stop_loss_percent*100:.1f}%)")

    def on_order_updated(self, order: Order) -> None:
        """Handle TP/SL order fills"""
        if not order.is_filled:
            return
        
        order_id = order.client_order_id
        
        # Check if this is a TP or SL order
        if hasattr(self, 'active_tp_order_id') and order_id == self.active_tp_order_id:
            self.log.info(f"TAKE-PROFIT FILLED at {order.price}")
            self._handle_position_close(reason="TP")
            
        elif hasattr(self, 'active_sl_order_id') and order_id == self.active_sl_order_id:
            self.log.warning(f"STOP-LOSS TRIGGERED at {order.price}")
            self._handle_position_close(reason="SL")
    
    def _cancel_all_grid_orders(self):
        """Cancel all grid orders when a position is opened"""
        working_orders = self.cache.orders_working(instrument_id=self.instrument_id)
        
        for order in working_orders:
            if order.is_open and order.client_order_id in self.grid_order_ids:
                self.cancel_order(order)
                self.log.debug(f"Canceling grid order: {order.client_order_id}")
        
        # Clear grid tracking
        self.grid_order_ids.clear()
        self.grid_levels_by_order_id.clear()
        
        self.log.info("Cancelled all grid orders (single position mode)")
            
    def _cleanup_trade_orders(self, trade: GridTrade) -> None:
        """Clean up remaining orders for a trade"""
        # Cancel opposite order if still open
        if trade.tp_order_id and trade.tp_order_id in self.tp_sl_order_ids:
            tp_order = self.cache.order(trade.tp_order_id)
            if tp_order and tp_order.is_open:
                self.cancel_order(tp_order)
        
        if trade.sl_order_id and trade.sl_order_id in self.tp_sl_order_ids:
            sl_order = self.cache.order(trade.sl_order_id)
            if sl_order and sl_order.is_open:
                self.cancel_order(sl_order)

    def _check_funding_rate(self) -> None:
        """Check and consider funding rates in trading decisions"""
        if not self.consider_funding_rate:
            return
        
        # Placeholder for funding rate integration
        # In production, implement actual exchange API calls
        
        if self.last_funding_rate > Decimal("0.0005"):
            self.log.info(f"High positive funding rate: {self.last_funding_rate*100:.4f}% - Favor LONG trades")
        elif self.last_funding_rate < Decimal("-0.0005"):
            self.log.info(f"High negative funding rate: {self.last_funding_rate*100:.4f}% - Favor SHORT trades")

    def _check_and_close_excess(self):
        """Close excess position if it grows beyond single trade size"""
        position = self.cache.position_for_instrument(self.instrument_id)
        if not position:
            return
        
        current_qty = abs(float(position.quantity))
        single_trade_qty = float(self._make_quantity())
        
        # If position is more than 1.5x single trade size, close excess
        if current_qty > single_trade_qty * 1.5:
            excess_qty = current_qty - single_trade_qty
            
            self.log.warning(f"Position {current_qty:.4f} exceeds single trade limit ({single_trade_qty:.4f}), "
                           f"closing {excess_qty:.4f}")
            
            if position.quantity > 0:  # Long
                close_order = self.order_factory.market(
                    instrument_id=self.instrument_id,
                    order_side=OrderSide.SELL,
                    quantity=self.instrument.make_qty(excess_qty),
                    time_in_force=TimeInForce.GTC,
                    reduce_only=True,
                )
            else:  # Short
                close_order = self.order_factory.market(
                    instrument_id=self.instrument_id,
                    order_side=OrderSide.BUY,
                    quantity=self.instrument.make_qty(excess_qty),
                    time_in_force=TimeInForce.GTC,
                    reduce_only=True,
                )
            
            self.submit_order(close_order)
            
    def on_clock(self, timestamp: float) -> None:
        """Handle clock events for periodic checks"""
        if not self.enable_margin_monitoring or self.paused_due_to_risk or not self.grid_active:
            return

        now = time.time()
        if now - self.last_margin_check_time < 60:  # Reduced frequency to every 60 seconds
            return
        self.last_margin_check_time = now

        try:
            account = self.cache.account_for_venue(Venue("BINANCE"))
            if account:
                maint = account.margins_maint().get(USDT, Money(0, USDT)).as_decimal()
                margin_bal = account.margin_balance(USDT).as_decimal()
                if margin_bal > 0:
                    ratio = maint / margin_bal
                    if ratio > self.margin_safety_threshold:
                        self._flatten_and_pause(f"Margin ratio {ratio:.1%} > {self.margin_safety_threshold:.1%}")
        except Exception as e:
            self.log.error(f"Margin check failed: {e}")

    def on_stop(self) -> None:
        """Clean shutdown procedure"""
        self.log.info("[SHUTDOWN] Canceling all open orders and flattening positions...")

        # Cancel all working orders
        for order in self.cache.orders_working(instrument_id=self.instrument_id):
            if order.is_open:
                self.cancel_order(order)

        # Flatten any open position
        position = self.cache.position_for_instrument(self.instrument_id)
        if position and not position.is_closed:
            if position.quantity > 0:  # Long
                self.submit_order(
                    MarketOrder(
                        instrument_id=self.instrument_id,
                        side=OrderSide.SELL,
                        quantity=position.quantity,
                        time_in_force=TimeInForce.GTC,
                        reduce_only=True,
                    )
                )
            elif position.quantity < 0:  # Short
                self.submit_order(
                    MarketOrder(
                        instrument_id=self.instrument_id,
                        side=OrderSide.BUY,
                        quantity=-position.quantity,
                        time_in_force=TimeInForce.GTC,
                        reduce_only=True,
                    )
                )

        # Clear all tracking
        self.grid_order_ids.clear()
        self.tp_sl_order_ids.clear()
        self.grid_trades.clear()
        
        # Log performance summary
        if self.performance_tracker.total_trades > 0:
            self.log.info(f"[PERFORMANCE] Total Trades: {self.performance_tracker.total_trades}, "
                         f"Win Rate: {self.performance_tracker.win_rate:.1%}, "
                         f"Total P&L: {self.performance_tracker.total_pnl:.4f}")

        self.log.info("[SHUTDOWN] Cleanup commands sent. Bot stopping.")


class PerformanceTracker:
    """Simple performance tracking"""
    def __init__(self):
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = Decimal("0")
        self.trades = []
    
    def add_trade(self, entry_price: Decimal, exit_price: Decimal, quantity: Quantity, 
                  side: OrderSide, profit: Decimal):
        """Add a completed trade to performance tracking"""
        self.total_trades += 1
        
        if profit > 0:
            self.winning_trades += 1
        
        self.total_pnl += profit
        
        # Store trade details
        self.trades.append({
            'entry_price': entry_price,
            'exit_price': exit_price,
            'quantity': quantity,
            'side': side,
            'profit': profit,
            'timestamp': time.time()
        })
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate"""
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades
    
    @property
    def avg_profit(self) -> Decimal:
        """Calculate average profit per trade"""
        if self.total_trades == 0:
            return Decimal("0")
        return self.total_pnl / Decimal(str(self.total_trades))