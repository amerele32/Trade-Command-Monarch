# utils/trailing_stop.py

import threading
import time
from utils.data_fetcher import get_session
from config import IG_API_BASE_URL

def monitor_position(deal_ref, epic, direction, atr, initial_sl):
    """
    Monitors a live spread-bet position and updates its stop-loss to trail the price by 1×ATR.
    """
    sl = initial_sl
    while True:
        time.sleep(30)  # check every 30 seconds
        session = get_session()
        try:
            # Fetch the latest 1-minute bar to get the current close price
            resp = session.get(
                f"{IG_API_BASE_URL}/prices/{epic}/HISTORICAL/1MINUTE",
                params={"max": 1},
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json().get("prices", []) or resp.json().get("candles", [])
            if not data:
                continue
            last_price = data[-1]["close"]
        except Exception:
            continue

        # Calculate a new stop-loss one ATR behind the current price
        new_sl = (last_price - atr) if direction == "buy" else (last_price + atr)

        # Only move the stop in the favorable direction
        if direction == "buy" and new_sl > sl:
            payload = {"dealReference": deal_ref, "stopLevel": new_sl}
            session.put(f"{IG_API_BASE_URL}/positions/{deal_ref}", json=payload)
            sl = new_sl
        elif direction == "sell" and new_sl < sl:
            payload = {"dealReference": deal_ref, "stopLevel": new_sl}
            session.put(f"{IG_API_BASE_URL}/positions/{deal_ref}", json=payload)
            sl = new_sl
