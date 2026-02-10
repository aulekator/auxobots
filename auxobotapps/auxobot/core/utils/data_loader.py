from pathlib import Path
import pandas as pd
from nautilus_trader.model.data import BarType
from nautilus_trader.persistence.wranglers import BarDataWrangler
 
def load_bars_from_csv(
    csv_path: Path | str,
    instrument,
    bar_type_str: str = None,
    price_columns: list[str] = None,
) -> list:
    """
    Load 1-minute bar data from a Binance-style CSV and convert it to Nautilus Bar objects.

    Expected CSV columns: open_time, open, high, low, close, volume (and possibly others)

    Parameters
    ----------
    csv_path : Path or str
        Path to the CSV file.
    instrument : Instrument
        The Nautilus instrument (e.g. SOLUSDT-PERP.BINANCE)
    bar_type_str : str, optional
        BarType as string, e.g. "SOLUSDT-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL"
        If None, will be inferred from instrument.
    price_columns : list[str], optional
        Columns to use for OHLCV. Default: ["open", "high", "low", "close", "volume"]

    Returns
    -------
    list of Bar objects
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    df = pd.read_csv(csv_path)

    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.set_index("timestamp")

    # Select and cast OHLCV
    if price_columns is None:
        price_columns = ["open", "high", "low", "close", "volume"]
    df = df[price_columns].astype("float64")

    df = df.sort_index()

    # Create BarType
    if bar_type_str is None:
        bar_type_str = f"{instrument.id.value}-1-MINUTE-LAST-EXTERNAL"
    bar_type = BarType.from_str(bar_type_str)

    # Process into bars
    wrangler = BarDataWrangler(bar_type=bar_type, instrument=instrument)
    bars = wrangler.process(df)

    print(f"Loaded {len(bars):,} bars from {csv_path.name}")
    return bars