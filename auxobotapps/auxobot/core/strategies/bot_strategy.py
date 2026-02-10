# ema_cross_bracket_algo_fixed.py

from decimal import Decimal
from typing import Any

from nautilus_trader.common.enums import LogColor
from nautilus_trader.config import PositiveFloat
from nautilus_trader.config import PositiveInt
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.core.data import Data
from nautilus_trader.core.message import Event
from nautilus_trader.indicators import AverageTrueRange          # <-- Fixed import
from nautilus_trader.indicators import ExponentialMovingAverage  # <-- Fixed import
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price
from nautilus_trader.model.orders import OrderList
from nautilus_trader.trading.strategy import Strategy


class EMACrossBracketAlgoConfig(StrategyConfig, frozen=True):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    atr_period: PositiveInt = 20
    fast_ema_period: PositiveInt = 10
    slow_ema_period: PositiveInt = 20
    bracket_distance_atr: PositiveFloat = 2.0   # Good for crypto volatility
    close_positions_on_stop: bool = True


class EMACrossBracketAlgo(Strategy):
    def __init__(self, config: EMACrossBracketAlgoConfig) -> None:
        PyCondition.is_true(
            config.fast_ema_period < config.slow_ema_period,
            f"{config.fast_ema_period=} must be less than {config.slow_ema_period=}",
        )
        super().__init__(config)

        self.instrument: Instrument | None = None

        self.atr = AverageTrueRange(config.atr_period)
        self.fast_ema = ExponentialMovingAverage(config.fast_ema_period)
        self.slow_ema = ExponentialMovingAverage(config.slow_ema_period)

    def on_start(self) -> None:
        self.instrument = self.cache.instrument(self.config.instrument_id)
        if self.instrument is None:
            self.log.error(f"Could not find instrument for {self.config.instrument_id}")
            self.stop()
            return

        self.register_indicator_for_bars(self.config.bar_type, self.atr)
        self.register_indicator_for_bars(self.config.bar_type, self.fast_ema)
        self.register_indicator_for_bars(self.config.bar_type, self.slow_ema)

        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        self.log.info(repr(bar), LogColor.CYAN)

        if not self.indicators_initialized():
            self.log.info(
                f"Waiting for indicators to warm up [{self.cache.bar_count(self.config.bar_type)} bars]",
                color=LogColor.BLUE,
            )
            return

        if bar.is_single_price():
            return

        # BUY
        if self.fast_ema.value >= self.slow_ema.value:
            if self.portfolio.is_flat(self.config.instrument_id):
                self.cancel_all_orders(self.config.instrument_id)
                self.buy(bar)
            elif self.portfolio.is_net_short(self.config.instrument_id):
                self.close_all_positions(self.config.instrument_id)
                self.cancel_all_orders(self.config.instrument_id)
                self.buy(bar)

        # SELL
        elif self.fast_ema.value < self.slow_ema.value:
            if self.portfolio.is_flat(self.config.instrument_id):
                self.cancel_all_orders(self.config.instrument_id)
                self.sell(bar)
            elif self.portfolio.is_net_long(self.config.instrument_id):
                self.close_all_positions(self.config.instrument_id)
                self.cancel_all_orders(self.config.instrument_id)
                self.sell(bar)

    def buy(self, bar: Bar) -> None:
        if not self.instrument:
            return

        distance = self.config.bracket_distance_atr * self.atr.value

        order_list = self.order_factory.bracket(
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.config.trade_size),
            entry_order_type=OrderType.MARKET,
            sl_trigger_price=self.instrument.make_price(bar.close - distance),
            tp_price=self.instrument.make_price(bar.close + distance),
        )

        self.submit_order_list(order_list)

    def sell(self, bar: Bar) -> None:
        if not self.instrument:
            return

        distance = self.config.bracket_distance_atr * self.atr.value

        order_list = self.order_factory.bracket(
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(self.config.trade_size),
            entry_order_type=OrderType.MARKET,
            sl_trigger_price=self.instrument.make_price(bar.close + distance),
            tp_price=self.instrument.make_price(bar.close - distance),
        )

        self.submit_order_list(order_list)

    def on_stop(self) -> None:
        self.cancel_all_orders(self.config.instrument_id)
        self.close_all_positions(self.config.instrument_id)
        self.unsubscribe_bars(self.config.bar_type)

    def on_reset(self) -> None:
        self.atr.reset()
        self.fast_ema.reset()
        self.slow_ema.reset()

    def on_save(self) -> dict:
        return {}

    def on_load(self, state: dict) -> None:
        pass

    def on_dispose(self) -> None:
        pass