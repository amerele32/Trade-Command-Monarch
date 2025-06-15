# utils/trade_executor.py

import os
import json
import logging
import time
from threading import Thread

from utils.journal import log_trade
from utils.data_fetcher import get_session
from utils.trailing_stop import monitor_position
from config import INITIAL_BALANCE, RISK_PCT, MARKET_INFO, IG_API_BASE_URL

# Path to persist balance
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
BALANCE_FILE = os.path.join(BASE_DIR, "balance.json")

def load_balance():
    """Load or initialize the demo balance."""
    if os.path.exists(BALANCE_FILE):
        try:
            with open(BALANCE_FILE, "r") as f:
                return json.load(f).get("balance", INITIAL_BALANCE)
        except Exception:
            logging.warning("Could not read balance.json; resetting to INITIAL_BALANCE.")
    save_balance(INITIAL_BALANCE)
    return INITIAL_BALANCE

def save_balance(balance):
    """Persist the updated balance."""
    try:
        with open(BALANCE_FILE, "w") as f:
            json.dump({"balance": balance}, f)
    except Exception as e:
        logging.error("Failed writing balance.json: %s", e)

# In-memory balance, loaded once at import
_balance = load_balance()

def place_trade(market, direction, sl, tp, confidence, strategy):
    """
    Calculate dynamic position size (1% risk), place a live IG spread-bet order,
    then spin up a trailing-stop monitor thread and log the trade.
    """
    global _balance

    # 1. Derive ATR & entry price from SL/TP
    atr = abs(tp - sl) / 3.0
    if atr <= 0:
        logging.error("Invalid SL/TP => ATR=%s for %s", atr, market)
        return

    entry = sl + atr if tp > sl else sl - atr

    # 2. Load market metadata
    info = MARKET_INFO.get(market)
    if not info:
        logging.error("No MARKET_INFO for %s", market)
        return
    min_size    = info["min_size"]
    point_value = info["point_value"]

    # 3. Compute raw & rounded position size
    risk_amount = _balance * RISK_PCT
    raw_size    = risk_amount / (atr * point_value)
    size = (raw_size // min_size) * min_size

    if size < min_size:
        logging.warning("Calculated size %.4f < min_size %.4f for %s; skipping", size, min_size, market)
        return

    # 4. Place the live order via IG REST API
    session = get_session()
    payload = {
        "epic": market,
        "direction": direction.upper(),
        "size": size,
        "orderType": "MARKET",
        "stopLevel": sl,
        "limitLevel": tp
    }
    deal_ref = None
    try:
        resp = session.post(f"{IG_API_BASE_URL}/positions/otc", json=payload, timeout=10)
        resp.raise_for_status()
        deal_ref = resp.json().get("dealReference")
        logging.info("Live order placed: dealRef=%s", deal_ref)
        # 5. Start the trailing‐stop monitor thread
        Thread(
            target=monitor_position,
            args=(deal_ref, market, direction, atr, sl),
            daemon=True
        ).start()
    except Exception as e:
        logging.error("Live order failed for %s: %s", market, e)

    # 6. Log the trade (CSV journal)
    log_trade(market, direction, sl, tp, confidence, strategy)

    # Note: Balance update on close happens elsewhere when P/L is known
