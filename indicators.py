# utils/indicators.py

import pandas as pd

def ema_cross_signal(data):
    """
    Returns a simple EMA crossover signal on provided OHLC data.
    """
    df = pd.DataFrame(data)
    if len(df) < 20:
        return None
    df['ema_fast'] = df['close'].ewm(span=10).mean()
    df['ema_slow'] = df['close'].ewm(span=20).mean()
    if df['ema_fast'].iloc[-1] > df['ema_slow'].iloc[-1]:
        return {
            'direction': 'buy',
            'price': df['close'].iloc[-1],
            'ATR': df['close'].rolling(14).std().iloc[-1]
        }
    if df['ema_fast'].iloc[-1] < df['ema_slow'].iloc[-1]:
        return {
            'direction': 'sell',
            'price': df['close'].iloc[-1],
            'ATR': df['close'].rolling(14).std().iloc[-1]
        }
    return None

def is_trend_up(data):
    """
    Determines if the higher timeframe is in an uptrend (EMA fast > EMA slow).
    """
    df = pd.DataFrame(data)
    if len(df) < 20:
        return False
    ema_fast = df['close'].ewm(span=10).mean().iloc[-1]
    ema_slow = df['close'].ewm(span=20).mean().iloc[-1]
    return ema_fast > ema_slow

def is_trend_down(data):
    """
    Determines if the higher timeframe is in a downtrend (EMA fast < EMA slow).
    """
    df = pd.DataFrame(data)
    if len(df) < 20:
        return False
    ema_fast = df['close'].ewm(span=10).mean().iloc[-1]
    ema_slow = df['close'].ewm(span=20).mean().iloc[-1]
    return ema_fast < ema_slow

def vwap(data):
    """
    Compute session VWAP: cumulative (price * volume) / cumulative volume.
    Returns the latest VWAP level or None if insufficient data.
    """
    df = pd.DataFrame(data)
    if 'volume' not in df.columns or 'close' not in df.columns or df['volume'].sum() == 0:
        return None
    cum_pv = (df['close'] * df['volume']).cumsum()
    cum_v  = df['volume'].cumsum()
    return (cum_pv / cum_v).iloc[-1]
