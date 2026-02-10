import logging
from decimal import Decimal
from pathlib import Path

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.config import LoggingConfig, RiskEngineConfig
from nautilus_trader.model.currencies import USDT, SOL
from nautilus_trader.model.objects import Money
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue, TraderId  

from ..utils.custom_config import CustomTestInstrumentProvider
from ..utils.data_loader import load_bars_from_csv
from ..strategies.bactest_grid_strategy import GridStrategy, GridStrategyConfig

logger = logging.getLogger(__name__)


def run_nautilus_backtest(
    usdt_balance: Decimal = Decimal("1000"),
    sol_amount: Decimal = Decimal("0"),
    grid_levels: int = 8,
    trade_size: Decimal = Decimal("1.000"),
    grid_profit: float = 1.2,
    grid_offset: float = 0.16,
    csv_path: Path | str = None,
) -> dict:
    if csv_path is None:
        raise ValueError("CSV path is required")
    csv_path = Path(csv_path)

    try:
        config = BacktestEngineConfig(
            trader_id=TraderId("GRID-BACKTESTER-001"),
            logging=LoggingConfig(log_level="INFO", log_colors=True, use_pyo3=False),
            risk_engine=RiskEngineConfig(bypass=True),
        )

        engine = BacktestEngine(config=config)

        # Fixed: Use Venue("BINANCE") directly
        engine.add_venue(
            venue=Venue("BINANCE"),
            oms_type=OmsType.NETTING,
            account_type=AccountType.MARGIN,
            starting_balances=[Money(usdt_balance, USDT), Money(sol_amount, SOL)],
            base_currency=None,
        )

        instrument = CustomTestInstrumentProvider.solusdt_perp_binance()
        engine.add_instrument(instrument)

        bars = load_bars_from_csv(
            csv_path=csv_path,
            instrument=instrument,
            bar_type_str="SOLUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL",
        )

        # ONLY ADD BARS — DYNAMIC GRID CENTERS ON FIRST BAR CLOSE
        engine.add_data(bars)

        logger.info(f"Loaded {len(bars)} bars — dynamic grid will center on first bar close")

        # DYNAMIC GRID CONFIG — NO lower/upper_price
        strategy_config = GridStrategyConfig(
            instrument_id=instrument.id,
            grid_levels=grid_levels,
            order_quantity=trade_size,
            grid_offset=grid_offset,
            grid_profit=grid_profit,
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
        )

        strategy = GridStrategy(config=strategy_config)
        engine.add_strategy(strategy)

        engine.run()

        # === Results ===
        account_report_df = engine.trader.generate_account_report(Venue("BINANCE"))
        usdt_rows = account_report_df[account_report_df['currency'] == 'USDT']
        ending_usdt = float(usdt_rows.iloc[-1]['total'])

        starting_usdt = float(usdt_balance)
        total_pnl = ending_usdt - starting_usdt
        pnl_percent = (total_pnl / starting_usdt) * 100 if starting_usdt > 0 else 0

        stats = engine.portfolio.analyzer.get_performance_stats_pnls(USDT)
        returns_stats = engine.portfolio.analyzer.get_performance_stats_returns()

        win_rate = stats.get('Win Rate', 0.0) * 100
        profit_factor = returns_stats.get('profit_factor', 0.0)
        expectancy = stats.get('Expectancy', 0.0)
        avg_win = stats.get('Avg Winner', 0.0)
        avg_loss = abs(stats.get('Avg Loser', 0.0))
        max_win = stats.get('Max Winner', 0.0)
        max_loss = abs(stats.get('Max Loser', 0.0))
        sharpe = returns_stats.get('sharpe_ratio') or 'N/A'

        summary = f"""
        **Dynamic Grid Backtest Results**
        - Run ID: `{engine.run_id}`
        - Grid Levels: {grid_levels} per side
        - Offset: ±{grid_offset * 100:.1f}%
        - Risk per Level: ~${float(trade_size):.2f} USDT notional
        - Profit Target: {grid_profit:.1f}% per cycle
        - Bars: {len(bars)}
        """.strip()

        account_summary = f"""
        **Account**
        - Starting: **${starting_usdt:,.2f} USDT**
        - Ending: **${ending_usdt:,.2f} USDT**
        - PnL: **{'+' if total_pnl >= 0 else '-'}${abs(total_pnl):,.2f}** ({'+' if pnl_percent >= 0 else '-'}{abs(pnl_percent):.2f}%)
        """.strip()

        performance = f"""
        **Performance**
        - Win Rate: **{win_rate:.1f}%**
        - Profit Factor: **{profit_factor:.2f}**
        - Expectancy: **{expectancy:.2f} USDT**
        - Avg Win: **+${avg_win:.2f}**
        - Avg Loss: **−${avg_loss:.2f}**
        - Max Win: **+${max_win:.2f}**
        - Max Loss: **−${max_loss:.2f}**
        - Sharpe: **{sharpe}**
        - Total Trades: **{engine.cache.orders_total_count()}**
        """.strip()

        engine.reset()
        engine.dispose()

        return {
            "summary": summary,
            "account_report": account_summary,
            "performance_report": performance,
            "metrics": {
                "starting_balance": float(starting_usdt),
                "ending_balance": float(ending_usdt),
                "total_pnl": float(total_pnl),
                "total_return_percent": float(pnl_percent),
                "win_rate_percent": float(win_rate),
                "total_trades": engine.cache.orders_total_count(),
                "sharpe_ratio": sharpe if sharpe != 'N/A' else None,
                "bars_loaded": len(bars),
            }
        }

    except Exception as e:
        logger.exception("Backtest failed")
        raise RuntimeError(f"Backtest failed: {str(e)}") from e