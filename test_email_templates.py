# test_email_templates.py

from utils.emailer import (
    send_trade_placed_email,
    send_trade_outcome_email,
    send_bot_offline_email,
    send_crash_email,
    send_daily_summary_email,
    send_weekly_summary_email
)

# 1. Trade Placed
send_trade_placed_email(
    market="CS.D.NAS100.MINI.IP",
    direction="buy",
    size=100,
    sl=1234.5,
    tp=1250.0,
    confidence=82,
    strategy="Momentum Breakout"
)

# 2. Trade Won
send_trade_outcome_email(
    market="CS.D.SPX.MINI.IP",
    direction="sell",
    entry_price=4000.0,
    exit_price=3950.0,
    profit=500.0
)

# 3. Trade Lost
send_trade_outcome_email(
    market="CS.D.DAX.MINI.IP",
    direction="buy",
    entry_price=15000.0,
    exit_price=14900.0,
    profit=-100.0
)

# 4. Bot Offline Notification
send_bot_offline_email()

# 5. Crash Notification
send_crash_email("This is a TEST exception message.")

# 6. Daily Summary
send_daily_summary_email()

# 7. Weekly Summary
send_weekly_summary_email()

print("Test emails sent. Check your inbox!")
