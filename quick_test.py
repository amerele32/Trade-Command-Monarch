# quick_test.py

import time
from utils.data_fetcher import authenticate
from utils.stream_fetcher import start_streaming, get_stream_bars
from config import MARKETS

def main():
    # 1. Authenticate and start streaming
    session = authenticate()
    print("Authenticated. Starting Lightstreamer streaming...")
    start_streaming(
        session.headers["X-IG-API-KEY"],
        session.headers["CST"],
        session.headers["X-SECURITY-TOKEN"],
        MARKETS
    )

    # 2. Wait a little to accumulate ticks
    print("Collecting ticks for 30 seconds...")
    time.sleep(30)

    # 3. Retrieve and display any aggregated 5-minute bars
    for epic in MARKETS:
        bars = get_stream_bars(epic, "5MINUTE")
        print(f"{epic} – Streaming 5-minute bars collected: {len(bars)}")
        if bars:
            print("Sample bar:", bars[-1])

if __name__ == "__main__":
    main()
