# utils/structure.py

def detect_swing_breaks(candles):
    """
    Identify clean 3-candle swing breakouts/breakdowns:
    - Bullish: three rising highs then breakout above the highest.
    - Bearish: three falling lows then breakdown below the lowest.
    """
    signals = []
    for i in range(3, len(candles)):
        prev3  = candles[i-3:i]
        highs  = [c["high"] for c in prev3]
        lows   = [c["low"]  for c in prev3]
        current = candles[i]

        # Bullish swing breakout
        if highs[0] < highs[1] < highs[2] and current["close"] > highs[2]:
            signals.append({
                "direction":    "buy",
                "price":        current["close"],
                "ATR":          current["ATR"],
                "breakout":     True,
                "volume":       current["volume"],
                "avg_volume":   current["avg_volume"],
                "ema_distance": current["ema_distance"],
                "session":      current["session"]
            })

        # Bearish swing breakdown
        if lows[0] > lows[1] > lows[2] and current["close"] < lows[2]:
            signals.append({
                "direction":    "sell",
                "price":        current["close"],
                "ATR":          current["ATR"],
                "breakout":     True,
                "volume":       current["volume"],
                "avg_volume":   current["avg_volume"],
                "ema_distance": current["ema_distance"],
                "session":      current["session"]
            })

    return signals

def detect_wick_rejections(candles):
    """
    Identify high-quality wick rejections:
    - Wick length ≥ 1.5×ATR and body ≤ 0.3×ATR.
    """
    signals = []
    for c in candles:
        body = abs(c["close"] - c["open"])
        # Wick calculation depends on bar direction
        if c["close"] < c["open"]:
            wick = max(c["high"] - c["close"], c["high"] - c["open"])
        else:
            wick = max(c["open"] - c["low"], c["close"] - c["low"])
        atr = c["ATR"]

        if wick >= 1.5 * atr and body <= 0.3 * atr:
            signals.append({
                "direction":    "sell" if c["close"] < c["open"] else "buy",
                "price":        c["close"],
                "ATR":          atr,
                "wick_ratio":   wick / body if body > 0 else float("inf"),
                "body_size":    body,
                "wick_size":    wick,
                "volume":       c["volume"],
                "avg_volume":   c["avg_volume"],
                "ema_distance": c["ema_distance"],
                "trend_state":  c["trend_state"],
                "session":      c["session"]
            })

    return signals

def confirm_structure(candles, signal):
    """
    Basic market structure check:
    - For longs: last close > previous close.
    - For shorts: last close < previous close.
    """
    if len(candles) < 2:
        return True
    last_close = candles[-1]["close"]
    prev_close = candles[-2]["close"]
    if signal.get("direction") == "buy":
        return last_close > prev_close
    else:
        return last_close < prev_close
