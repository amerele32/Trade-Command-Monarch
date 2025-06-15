# utils/session_timer.py
from datetime import datetime
def is_trading_session():
    now = datetime.utcnow()
    total = now.hour*60 + now.minute
    return (510 <= total <= 660) or (870 <= total <= 1020)
