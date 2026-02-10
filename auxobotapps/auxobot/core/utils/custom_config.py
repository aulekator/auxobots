from decimal import Decimal
from nautilus_trader.model.currencies import SOL, USDT
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.instruments import CryptoPerpetual
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.test_kit.providers import TestInstrumentProvider


class CustomTestInstrumentProvider(TestInstrumentProvider):

    @staticmethod
    def solusdt_perp_binance() -> CryptoPerpetual: 
        """
        Return the Binance Futures SOLUSDT-PERP instrument for backtesting.

        Returns
        -------
        CryptoPerpetual
        """
        return CryptoPerpetual(
            instrument_id=InstrumentId(
                symbol=Symbol("SOLUSDT-PERP"),
                venue=Venue("BINANCE"),
            ),
            raw_symbol=Symbol("SOLUSDT"),
            base_currency=SOL,
            quote_currency=USDT,
            settlement_currency=USDT,
            is_inverse=False,
            price_precision=2,          # Common for SOL prices
            size_precision=3,           # 0.001 SOL
            price_increment=Price.from_str("0.01"),
            size_increment=Quantity.from_str("0.001"),
            max_quantity=Quantity.from_str("10000.000"),
            min_quantity=Quantity.from_str("0.001"),
            max_notional=None,
            min_notional=Money(5.00, USDT),  # Binance standard threshold
            max_price=Price.from_str("1000.00"),     # Realistic upper bound
            min_price=Price.from_str("0.01"),
            margin_init=Decimal("0.05"),      # Example: 20x leverage
            margin_maint=Decimal("0.025"),
            maker_fee=Decimal("0.0002"),
            taker_fee=Decimal("0.0004"),
            ts_event=0,                      # Or keep old if needed
            ts_init=0,
        )