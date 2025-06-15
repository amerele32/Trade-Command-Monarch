# utils/stream_fetcher.py

import threading
import time
from datetime import datetime, timedelta
from collections import deque, defaultdict

from lightstreamer.client import LightstreamerClient, Subscription

# Tick buffers and bar aggregators
_tick_buffers = defaultdict(lambda: deque())
_bar_buffers = defaultdict(lambda: defaultdict(lambda: deque(maxlen=100)))
_lock = threading.Lock()

def _on_item_update(item_update):
    epic = item_update.getItemName()
    price = float(item_update.getValue("LTP") or 0)
    ts = datetime.utcnow()
    with _lock:
        _tick_buffers[epic].append((ts, price))

def start_streaming(api_key, cst, token, epics):
    """
    Connects to IG's Lightstreamer demo endpoint, subscribes to epics,
    and starts a background thread to aggregate 5-minute bars.
    """
    client = LightstreamerClient("https://pushlightstream-demo.ig.com", "QUOTE_ADAPTER")

    # Inject IG authentication headers
    client.connectionDetails.httpExtraHeaders = {
        "X-IG-API-KEY": api_key,
        "CST": cst,
        "X-SECURITY-TOKEN": token
    }

    # Establish connection
    client.connect()

    # Subscribe to Last Traded Price (LTP) updates for each epic
    sub = Subscription("MERGE", epics, ["LTP"])
    sub.setDataAdapter("QUOTE_ADAPTER")
    sub.setRequestedSnapshot("no")
    sub.addListener(_on_item_update)
    client.subscribe(sub)

    # Launch bar aggregation thread
    threading.Thread(target=_aggregate_bars, args=(epics,), daemon=True).start()

def _aggregate_bars(epics):
    """
    Every 5 minutes, builds OHLCV bars from tick buffer.
    """
    while True:
        now = datetime.utcnow()
        next_bound = (now + timedelta(minutes=5)).replace(second=0, microsecond=0)
        time.sleep((next_bound - now).total_seconds())

        with _lock:
            for epic in epics:
                ticks = list(_tick_buffers[epic])
                _tick_buffers[epic].clear()
                if not ticks:
                    continue
                prices = [p for _, p in ticks]
                bar = {
                    "timestamp": next_bound.isoformat(),
                    "open": prices[0],
                    "high": max(prices),
                    "low": min(prices),
                    "close": prices[-1],
                    "volume": len(prices)
                }
                _bar_buffers[epic]["5MINUTE"].append(bar)

def get_stream_bars(epic, resolution):
    """
    Returns aggregated bars for the given resolution.
    Only "5MINUTE" is supported.
    """
    if resolution != "5MINUTE":
        return []
    with _lock:
        return list(_bar_buffers[epic].get("5MINUTE", []))
