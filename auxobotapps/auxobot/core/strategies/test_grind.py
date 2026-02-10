# grid_strategy.py (FINAL WORKING VERSION)

from decimal import Decimal
from typing import List

from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.trading.strategy import Strategy


class GridStrategyConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    user_id: int = None 
    bar_type: BarType
    lower_price: float
    upper_price: float
    grid_levels: int = 15
    order_quantity: Decimal = Decimal("1.000")  # USDT notional per level
    grid_profit: float = 1.0


class GridStrategy(Strategy):
    def __init__(self, config: GridStrategyConfig) -> None:
        super().__init__(config)

        PyCondition.positive(config.upper_price - config.lower_price, "price range")
        PyCondition.positive(config.grid_levels, "grid_levels")

        # Store instrument_id for cache access
        self.instrument_id = config.instrument_id

        self.instrument: Instrument | None = None

        self.grid_spacing = (config.upper_price - config.lower_price) / config.grid_levels
        self.grid_profit = Decimal(str(config.grid_profit))
        self.order_quantity = config.order_quantity  # USDT notional

        self.lower_bound = Decimal(str(config.lower_price))
        self.upper_bound = Decimal(str(config.upper_price))

        self.active_buy_orders: List[str] = []
        self.active_sell_orders: List[str] = []
        self.grid_active = False

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.instrument_id)
        if self.instrument is None:
            self.log.error(f"Instrument not found: {self.instrument_id}")
            self.stop()
            return

        self.subscribe_bars(self.config.bar_type)
        self.log.info("Grid strategy started. Waiting for price to enter range...")

    def on_bar(self, bar: Bar) -> None:
        if not self.instrument:
            return

        current_price = Decimal(str(bar.close.as_double()))

        # === STOP LOSS: Price broke out of grid range → FULL SHUTDOWN ===
        if self.grid_active and (current_price < self.lower_bound or current_price > self.upper_bound):
            self.log.warning(
                f"PRICE BROKE GRID RANGE! Current: {current_price} | "
                f"Bounds: [{self.lower_bound}, {self.upper_bound}] → STOPPING BOT"
            )
            self.cancel_all_orders(self.instrument_id)
            self.close_all_positions(self.instrument_id)
            self.stop()
            return

        # === Place grid only once when price enters range ===
        if not self.grid_active and self.lower_bound <= current_price <= self.upper_bound:
            mid_price = float((self.lower_bound + self.upper_bound) / 2)
            self.place_grid(mid_price)
            self.grid_active = True

    def _make_price(self, raw_price: float) -> Price:
        rounded = self.instrument.make_price(raw_price)
        return Price(rounded, self.instrument.price_precision)

    def _make_quantity(self) -> Quantity:
        """Convert USDT notional to proper contract quantity using current price."""
        tick = self.cache.quote_tick(self.instrument_id)
        if tick is None:
            # Fallback: use instrument mid price or small default
            last_price = self.instrument.price_increment * 100.0
        else:
            last_price = tick.last_price.as_double()

        # Convert Decimal → float safely
        usdt_notional = float(self.order_quantity)
        contracts = usdt_notional / last_price
        return self.instrument.make_qty(contracts)

    def place_grid(self, mid_price: float) -> None:
        qty = self._make_quantity()

        self.log.info(
            f"Placing grid around {mid_price:.{self.instrument.price_precision}f} "
            f"with {self.config.grid_levels} levels each side"
        )

        # Buy orders below mid
        for i in range(1, self.config.grid_levels + 1):
            raw_price = mid_price - i * self.grid_spacing
            price = self._make_price(raw_price)
            order = self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.BUY,
                quantity=qty,
                price=price,
                post_only=True,
                time_in_force=TimeInForce.GTC,
            )
            self.submit_order(order)
            self.active_buy_orders.append(order.client_order_id)

        # Sell orders above mid
        for i in range(1, self.config.grid_levels + 1):
            raw_price = mid_price + i * self.grid_spacing
            price = self._make_price(raw_price)
            order = self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.SELL,
                quantity=qty,
                price=price,
                post_only=True,
                time_in_force=TimeInForce.GTC,
            )
            self.submit_order(order)
            self.active_sell_orders.append(order.client_order_id)

        self.log.info(f"Grid activated: {len(self.active_buy_orders)} buy + {len(self.active_sell_orders)} sell orders")

    def on_fill(self, fill) -> None:
        if not self.instrument or not self.grid_active:
            return

        order = fill.order
        filled_price = order.price.as_double()
        qty = order.quantity

        if order.side == OrderSide.BUY:
            target_price = self._make_price(filled_price + float(self.grid_profit))
            new_order = self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.SELL,
                quantity=qty,
                price=target_price,
                post_only=True,
                time_in_force=TimeInForce.GTC,
            )
            self.submit_order(new_order)
            self.log.info(f"Buy filled @ {filled_price:.{self.instrument.price_precision}f} → Sell @ {target_price}")

        elif order.side == OrderSide.SELL:
            target_price = self._make_price(filled_price - float(self.grid_profit))
            new_order = self.order_factory.limit(
                instrument_id=self.instrument_id,
                order_side=OrderSide.BUY,
                quantity=qty,
                price=target_price,
                post_only=True,
                time_in_force=TimeInForce.GTC,
            )
            self.submit_order(new_order)
            self.log.info(f"Sell filled @ {filled_price:.{self.instrument.price_precision}f} → Buy @ {target_price}")

    def on_stop(self) -> None:
        self.cancel_all_orders(self.instrument_id)
        self.close_all_positions(self.instrument_id)
        self.log.info("Grid strategy stopped safely — all orders canceled, positions closed.")