# utils/data_fetcher.py

import requests
import logging
import time
from config import IG_API_BASE_URL, IG_APP_KEY, IG_USERNAME, IG_PASSWORD

# Cache for higher‐timeframe candles
_htf_cache = {}

# Session state & auth timing
_session = None
_last_auth = 0
_AUTH_INTERVAL = 28 * 60  # seconds

def authenticate():
    """
    Log in to IG demo spreadbet API.
    """
    global _session, _last_auth
    session = requests.Session()
    session.headers.update({
        "X-IG-API-KEY": IG_APP_KEY,
        "Content-Type": "application/json; charset=UTF-8",
        "VERSION": "3"
    })
    payload = {"identifier": IG_USERNAME, "password": IG_PASSWORD}
    resp = session.post(f"{IG_API_BASE_URL}/session", json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    # IG demo sometimes omits accountType, so we skip enforcing it strictly
    acct_type = data.get("accountInfo", {}).get("accountType")
    if acct_type and acct_type != "SPREADBET":
        raise RuntimeError(f"Logged into wrong account type: {acct_type}")

    # Save session tokens for subsequent calls
    session.headers["CST"] = resp.headers.get("CST", "")
    session.headers["X-SECURITY-TOKEN"] = resp.headers.get("X-SECURITY-TOKEN", "")
    logging.info("Authenticated to IG demo API (spreadbet).")
    _session = session
    _last_auth = time.time()
    return session

def get_session():
    """
    Return a valid IG session, re-authenticating if needed.
    """
    global _session, _last_auth
    now = time.time()
    if _session is None or now - _last_auth > _AUTH_INTERVAL:
        return authenticate()
    return _session

def get_market_data(session, epic, resolution="5MINUTE", max_candles=100):
    """
    Fetch historical bar data via REST for the given epic and timeframe.
    Falls back to streaming‐aggregated bars if REST returns empty.
    """
    # Validate resolution
    valid_res = {"5MINUTE", "15MINUTE", "HOUR", "DAILY"}
    if resolution not in valid_res:
        raise ValueError(f"Invalid resolution: {resolution}")

    # Use cache for higher‐timeframes
    now = time.time()
    if resolution in ("15MINUTE", "HOUR"):
        key = (epic, resolution)
        ttl = {"15MINUTE": 900, "HOUR": 3600}[resolution]
        if key in _htf_cache and now - _htf_cache[key][0] < ttl:
            return _htf_cache[key][1]

    url = f"{IG_API_BASE_URL}/prices/{epic}/HISTORICAL/{resolution}"
    params = {"max": max_candles}
    attempt, wait = 0, 1

    while attempt < 3:
        resp = session.get(url, params=params, timeout=10)
        # If unauthorized, re-auth and retry
        if resp.status_code == 401:
            session = authenticate()
            attempt += 1
            continue
        # For 400/404, bail out
        if resp.status_code in (400, 404):
            logging.error("IG REST failed: %s %s", resp.status_code, resp.text)
            resp.raise_for_status()
        try:
            resp.raise_for_status()
        except Exception as e:
            logging.error("Error fetching %s %s: %s", epic, resolution, e)
            time.sleep(wait)
            wait *= 2
            attempt += 1
            continue

        j = resp.json()
        data = j.get("prices", []) or j.get("candles", [])
        # Cache HTF data
        if resolution in ("15MINUTE", "HOUR"):
            _htf_cache[key] = (now, data)

        # Fallback to streaming buffer if empty
        if not data and resolution in ("5MINUTE", "DAILY"):
            from utils.stream_fetcher import get_stream_bars
            data = get_stream_bars(epic, resolution)

        return data

    logging.error("Failed to fetch data for %s %s after retries", epic, resolution)
    return []

def get_prior_daily(session, epic):
    """
    Fetch the last two daily bars and return the prior session's high & low.
    """
    resp = session.get(
        f"{IG_API_BASE_URL}/prices/{epic}/HISTORICAL/DAILY",
        params={"max": 2}, timeout=10
    )
    resp.raise_for_status()
    j = resp.json()
    arr = j.get("prices", []) or j.get("candles", [])
    if len(arr) < 2:
        return None, None
    prior = arr[-2]
    return prior.get("high"), prior.get("low")
