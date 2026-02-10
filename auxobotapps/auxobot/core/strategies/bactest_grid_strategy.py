from decimal import Decimal
import time
from typing import Optional

from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import QuoteTick, TradeTick, Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId, Venue
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.currencies import USDT
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model.enums import PositionSide


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


class GridStrategy(Strategy):
    def __init__(self, config: GridStrategyConfig) -> None:
        super().__init__(config)

        self.instrument_id = config.instrument_id
        self.instrument: Optional[Instrument] = None

        self.grid_levels = config.grid_levels
        self.order_quantity = config.order_quantity
        self.base_grid_offset = Decimal(str(config.grid_offset))
        self.grid_profit = Decimal(str(config.grid_profit))
        self.recenter_drift = Decimal(str(config.recenter_drift_threshold))
        self.recenter_interval = config.recenter_interval_seconds

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

        self.enable_breakout_stop = config.enable_breakout_stop
        self.enable_exposure_limits = config.enable_exposure_limits
        self.enable_margin_monitoring = config.enable_margin_monitoring
        self.enable_trailing_stop = config.enable_trailing_stop
        self.enable_max_drawdown = config.enable_max_drawdown

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

        self.atr_period = 14
        self.atr_values = []
        self.prev_close: Optional[Decimal] = None

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.instrument_id)
        if not self.instrument:
            self.log.error(f"Instrument not found: {self.instrument_id}")
            self.stop()
            return

        bar_type = BarType.from_str(f"{self.instrument_id}-1-MINUTE-LAST-EXTERNAL")
        self.subscribe_bars(bar_type)
        self.subscribe_quote_ticks(self.instrument_id)
        self.subscribe_trade_ticks(self.instrument_id)

        self.log.info(f"Enhanced GridStrategy started for {self.instrument_id}")

    def on_bar(self, bar: Bar) -> None:
        # Use bar close as initial mid price if not set yet
        if self.current_mid_price is None:
            self._process_price_update(bar.close.as_decimal())
            return  # Skip ATR calc on very first bar if desired

        if self.prev_close is None:
            self.prev_close = bar.close
            return

        tr = max(
            bar.high - bar.low,
            abs(bar.high - self.prev_close),
            abs(bar.low - self.prev_close)
        )
        self.atr_values.append(tr)
        if len(self.atr_values) > self.atr_period:
            self.atr_values.pop(0)
        self.prev_close = bar.close

        # Optional: Also update mid price on every bar close for recentering checks
        self._process_price_update(bar.close.as_decimal())

    def _get_atr_multiplier(self) -> Decimal:
        if not self.atr_values or not self.current_mid_price:
            return Decimal("1")
        current_atr = sum(self.atr_values) / len(self.atr_values)
        atr_percent = current_atr / float(self.current_mid_price)
        return min(max(Decimal(str(atr_percent / 0.01)), Decimal("0.7")), Decimal("1.8"))

    def on_quote_tick(self, tick: QuoteTick) -> None:
        mid = (tick.bid_price + tick.ask_price) / Decimal("2")
        self._process_price_update(mid)

    def on_trade_tick(self, tick: TradeTick) -> None:
        if self.current_mid_price is None:
            self._process_price_update(Decimal(str(tick.price.as_double())))

    def _get_current_position_notional(self) -> tuple[Decimal, Decimal]:
        if not self.current_mid_price:
            return Decimal("0"), Decimal("0")

        long_n = short_n = Decimal("0")
        for position in self.cache.positions(instrument_id=self.instrument_id):
            if position.is_closed:
                continue
            notional = Decimal(str(abs(float(position.quantity)) * float(self.current_mid_price)))
            if position.side == PositionSide.LONG:
                long_n += notional
            elif position.side == PositionSide.SHORT:
                short_n += notional
        return long_n, short_n

    def _check_exposure_limits(self) -> bool:
        if not self.enable_exposure_limits or not self.grid_active:
            return True
        long_n, short_n = self._get_current_position_notional()
        total_n = long_n + short_n
        if long_n > self.max_long_notional or short_n > self.max_short_notional or total_n > self.max_total_notional:
            self.log.error(f"Exposure breach: Long={long_n}, Short={short_n}, Total={total_n}")
            return False
        return True
    
    def _check_drawdown(self) -> bool:
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
        if self.paused_due_to_risk:
            return
        self.log.warning(f"SAFETY TRIGGER: {reason} → Flattening + pausing")
        self.cancel_all_orders(self.instrument_id)
        self.close_all_positions(self.instrument_id)
        self.grid_active = False
        self.paused_due_to_risk = True
        self.last_pause_time = time.time()

    def _process_price_update(self, mid_price: Decimal) -> None:
        if self.current_mid_price is None:
            self._center_grid(mid_price)
            return

        self.current_mid_price = mid_price
        if self.highest_mid_since_start < mid_price:
            self.highest_mid_since_start = mid_price

        if self.paused_due_to_risk and self.enable_auto_resume:
            if (time.time() - self.last_pause_time > self.resume_cooldown and
                    self.original_lower and self.original_upper and
                    mid_price > self.original_lower * (Decimal("1") - self.resume_tolerance) and
                    mid_price < self.original_upper * (Decimal("1") + self.resume_tolerance)):
                self.log.info("Auto-resuming grid after cooldown + price sanity")
                self.paused_due_to_risk = False
                self._center_grid(mid_price)
                return

        if self.paused_due_to_risk:
            return

        if self.enable_breakout_stop and self.grid_active and self.lower_price and self.upper_price:
            lower_bound = self.lower_price * (Decimal("1") - self.breakout_threshold)
            upper_bound = self.upper_price * (Decimal("1") + self.breakout_threshold)
            if mid_price < lower_bound or mid_price > upper_bound:
                self._flatten_and_pause(f"Breakout ±{self.breakout_threshold:.0%}")
                return

        if not self._check_exposure_limits():
            self._flatten_and_pause("Exposure limits")
            return

        if not self._check_drawdown():
            self._flatten_and_pause("Max drawdown")
            return

        if self.enable_trailing_stop and self.grid_active:
            trail_low = self.highest_mid_since_start * (Decimal("1") - self.trailing_stop_threshold)
            if mid_price < trail_low:
                self._flatten_and_pause(f"Trailing stop {self.trailing_stop_threshold:.0%} from high")
                return

        now = time.time()
        if now - self.last_recenter_time > self.recenter_interval:
            drift = abs(mid_price - self.current_mid_price) / self.current_mid_price
            if drift > self.recenter_drift:
                self.log.info(f"Drift {drift:.1%} → Re-centering")
                self.cancel_all_orders(self.instrument_id)
                self._center_grid(mid_price)
                self.last_recenter_time = now

    def _center_grid(self, mid_price: Decimal) -> None:
        self.current_mid_price = mid_price
        if self.highest_mid_since_start < mid_price:
            self.highest_mid_since_start = mid_price

        offset = self.base_grid_offset
        if self.vol_adapt:
            offset *= self._get_atr_multiplier()

        half = offset / Decimal("2")
        self.lower_price = mid_price * (Decimal("1") - half)
        self.upper_price = mid_price * (Decimal("1") + half)
        if self.original_lower is None:
            self.original_lower = self.lower_price
            self.original_upper = self.upper_price

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

        self.log.info(
            f"Grid centered at {mid_price:.{self.instrument.price_precision}f} | "
            f"Range: {self.lower_price:.{self.instrument.price_precision}f} – {self.upper_price:.{self.instrument.price_precision}f} "
            f"(±{half * 100:.2f}%{' - adapted by ATR' if self.vol_adapt else ''})"
        )

        self._place_grid_orders()
        self.grid_active = True
        self.paused_due_to_risk = False

    def _make_price(self, raw_price: float) -> Price:
        return Price(self.instrument.make_price(raw_price), self.instrument.price_precision)

    def _make_quantity(self) -> Quantity:
        """
        Return a fixed Quantity in base asset (e.g., SOL) as specified in config.order_quantity.
        """
        raw_qty = self.order_quantity

        precision = self.instrument.size_precision

        # Create quantity with correct precision
        qty_value = float(raw_qty.quantize(Decimal(f"1.{''.join(['0'] * precision)}")))

        qty = Quantity(
            value=qty_value,
            precision=precision,
        )

        # Enforce minimum quantity if needed
        if qty < self.instrument.min_quantity:
            self.log.warning(
                f"Quantity {qty} below instrument min {self.instrument.min_quantity}. "
                f"Adjusting upward."
            )
            qty = self.instrument.min_quantity
        return qty

    def _place_grid_orders(self) -> None:
        qty = self._make_quantity()
        ratio = (self.upper_price / self.lower_price) ** (Decimal("1") / Decimal(str(self.grid_levels * 2)))

        for i in range(1, self.grid_levels + 1):
            buy_price_raw = float(self.current_mid_price * (ratio ** -Decimal(str(i))))
            buy_price = self._make_price(buy_price_raw)
            self.submit_order(self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.BUY,
                price=buy_price,
                quantity=qty,
                post_only=True,
                time_in_force=TimeInForce.GTC,
                # Remove client_order_id or pass None
            ))

            sell_price_raw = float(self.current_mid_price * (ratio ** Decimal(str(i))))
            sell_price = self._make_price(sell_price_raw)
            self.submit_order(self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.SELL,
                price=sell_price,
                quantity=qty,
                post_only=True,
                time_in_force=TimeInForce.GTC,
                # Remove client_order_id or pass None
            ))

        self.log.info(f"Placed {self.grid_levels * 2} geometric grid orders")
            
    def on_fill(self, fill) -> None:
        if not self.grid_active or self.paused_due_to_risk:
            return

        filled_price = Decimal(str(fill.order.price.as_double()))
        qty = fill.order.quantity

        if fill.order.side == OrderSide.BUY:
            target_raw = float(filled_price * (Decimal("1") + self.grid_profit / Decimal("100")))
            target_price = self._make_price(target_raw)
            self.submit_order(self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.SELL,
                price=target_price,
                quantity=qty,
                post_only=False,
                time_in_force=TimeInForce.GTC,
            ))
        elif fill.order.side == OrderSide.SELL:
            target_raw = float(filled_price * (Decimal("1") - self.grid_profit / Decimal("100")))
            target_price = self._make_price(target_raw)
            self.submit_order(self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.BUY,
                price=target_price,
                quantity=qty,
                post_only=False,
                time_in_force=TimeInForce.GTC,
            ))

    def on_clock(self, timestamp: float) -> None:
        if not self.enable_margin_monitoring or self.paused_due_to_risk or not self.grid_active:
            return

        now = time.time()
        if now - self.last_margin_check_time < 30:
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
        self.cancel_all_orders(self.instrument_id)
        self.close_all_positions(self.instrument_id)
        self.log.info("GridStrategy stopped – cleanup complete")