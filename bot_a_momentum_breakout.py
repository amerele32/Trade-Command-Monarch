from utils.health_check import record_bot_heartbeat, get_confidence_threshold
from utils.data_fetcher import get_session, get_market_data, get_prior_daily
from utils.filters import (
    volatility_ok,
    confidence_score,
    smart_trailing_stop,
    prior_session_breakout,
    vwap_bias
)
from utils.indicators import ema_cross_signal, is_trend_up, is_trend_down, vwap
from utils.structure import detect_swing_breaks  # Corrected function import
from utils.trade_executor import place_trade
from config import MARKETS

def run_momentum_bot():
    # Heartbeat for monitoring
    record_bot_heartbeat("momentum")

    session = get_session()
    min_conf = get_confidence_threshold()

    for epic in MARKETS:
        # 1) Fetch bars
        data_15m = get_market_data(session, epic, "15MINUTE")
        data_5m  = get_market_data(session, epic, "5MINUTE")
        data_1h  = get_market_data(session, epic, "HOUR")

        # 2) EMA-cross signal
        signal = ema_cross_signal(data_15m)
        if not signal:
            continue

        # 3) Market structure check
        if not confirm_structure(data_5m, signal):
            continue

        # 4) Prior-session extremes
        prior_high, prior_low = get_prior_daily(session, epic)
        if not prior_session_breakout(signal, prior_high, prior_low):
            continue

        # 5) Volatility filter
        if not volatility_ok(signal):
            continue

        # 6) VWAP bias on 1-hour
        current_vwap = vwap(data_1h)
        if not vwap_bias(signal, current_vwap):
            continue

        # 7) EMA confluence on 1-hour
        direction = signal["direction"]
        if direction == "buy":
            if not is_trend_up(data_1h):
                continue
        else:
            if not is_trend_down(data_1h):
                continue

        # 8) Confidence threshold
        score = confidence_score(signal)
        if score < min_conf:
            continue

        # 9) SL/TP & execute
        sl, tp = smart_trailing_stop(signal)
        place_trade(epic, direction, sl, tp, score, "Momentum")
