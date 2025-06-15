#!/usr/bin/env python3
# trade_command_pro_main.py

import sys
print("=== Trade Command Monarch script loading ===", file=sys.stdout)

import time
from datetime import datetime
import pytz

# --- 1. Core imports & health/email ---
from utils.session_timer import is_trading_session
from utils.health_check import check_health
from utils.emailer import (
    send_daily_summary_email,
    send_weekly_summary_email,
    send_bot_online_email,
    send_bot_offline_email,
    send_crash_email
)
from utils.controller import run_event
from config import MARKETS

# --- 2. Strategy bots ---
from bots.bot_a_momentum_breakout import run_momentum_bot
from bots.bot_b_wick_rejection import run_wick_bot
from bots.bot_c_trend_continuation import run_trend_bot

def main_loop():
    try:
        # 1. Startup notifications & prints
        print("🔁 Trade Command Monarch main loop starting…", file=sys.stdout)
        try:
            send_bot_online_email()
        except Exception as e:
            print(f"⚠️ Warning: send_bot_online_email failed: {e}", file=sys.stdout)

        # 2. Ensure bots are active by default
        run_event.set()

        offline_sent = False
        london = pytz.timezone("Europe/London")
        daily_sent = False
        weekly_sent = False

        # 3. Start market data fallback (no Lightstreamer import)
        from utils.data_fetcher import get_session
        session = get_session()
        print("🛰️ Connected to market data session…", file=sys.stdout)

        # 4. Main loop
        while True:
            try:
                now = datetime.now(london)

                # Execute each bot if flag is set and in trading hours
                if run_event.is_set() and is_trading_session():
                    run_momentum_bot()
                    run_wick_bot()
                    run_trend_bot()
                    # record_trade_time()  # <-- REMOVE or COMMENT OUT THIS LINE

                # Daily summary at 20:00 UK
                if now.hour == 20 and not daily_sent:
                    send_daily_summary_email()
                    daily_sent = True
                if now.hour < 20:
                    daily_sent = False

                # Weekly summary Friday 21:00 UK
                if now.weekday() == 4 and now.hour == 21 and not weekly_sent:
                    send_weekly_summary_email()
                    weekly_sent = True
                if now.weekday() != 4 or now.hour < 21:
                    weekly_sent = False

                # Health check
                check_health()

            except Exception as loop_err:
                print(f"❌ Loop error: {loop_err}", file=sys.stdout)
                try:
                    send_crash_email(str(loop_err))
                except Exception as e:
                    print(f"⚠️ send_crash_email failed: {e}", file=sys.stdout)

            time.sleep(60)

    except Exception as e:
        # Catch any startup errors
        print(f"🚨 Startup failed: {e}", file=sys.stdout)
        try:
            send_crash_email(f"Startup failed: {e}")
        except:
            print(f"⚠️ send_crash_email failed on startup: {e}", file=sys.stdout)
        raise

if __name__ == "__main__":
    main_loop()
