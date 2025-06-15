# utils/filters.py

"""
Filter functions for Trade Command Monarch:
- volatility_ok: ATR-based volatility filter
- confidence_score: 0-100 confidence rating
- smart_trailing_stop: static 1×ATR SL, 2×ATR TP
- within_market_conditions: restricts markets
- wick_logic_passed: basic wick logic
- regime_filter: market regime check
- prior_session_breakout: prior-day high/low filter
- vwap_bias: VWAP directional filter
"""

def volatility_ok(signal):
    atr = signal.get("ATR", 0)
    return 5 < atr < 25


def confidence_score(signal):
    score = 0
    if signal.get("breakout") or signal.get("wick_ratio", 0) > 2:
        score += 30
    if signal.get("volume", 0) > signal.get("avg_volume", 0):
        score += 20
    if signal.get("ema_distance", 0) > 5:
        score += 20
    if signal.get("session") in ["UK", "US"]:
        score += 20
    return min(score, 100)


def smart_trailing_stop(signal):
    direction = signal.get("direction")
    entry = signal.get("price", 0)
    atr = signal.get("ATR", 0)
    if direction == "buy":
        return entry - atr, entry + 2 * atr
    else:
        return entry + atr, entry - 2 * atr


def within_market_conditions(signal):
    return signal.get("market") in ["NAS100", "SPX500", "DAX40", "FTSE100"]


def wick_logic_passed(signal):
    return (
        signal.get("wick_ratio", 0) >= 2
        and signal.get("body_size", 0) <= signal.get("wick_size", 0)
    )


def regime_filter(signal):
    return signal.get("trend_state") in ["range", "transition"]


def prior_session_breakout(signal, prior_high, prior_low):
    price = signal.get("price")
    direction = signal.get("direction")
    if price is None or prior_high is None or prior_low is None:
        return False
    if direction == "buy":
        return price > prior_high
    else:
        return price < prior_low


def vwap_bias(signal, vwap_level):
    """
    Only accept long trades when price > VWAP,
    and short when price < VWAP.
    """
    price = signal.get("price")
    direction = signal.get("direction")
    if price is None or vwap_level is None:
        return False
    if direction == "buy":
        return price > vwap_level
    else:
        return price < vwap_level


def momentum_logic_passed(signal):
    """
    Example: Only trade if momentum filter is passed.
    You can expand logic as needed.
    """
    return signal.get("momentum", False) and signal.get("volume", 0) > signal.get("avg_volume", 0)

