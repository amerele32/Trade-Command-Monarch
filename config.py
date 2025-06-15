# config.py

IG_API_BASE_URL = "https://demo-api.ig.com/gateway/deal"
IG_APP_KEY       = "d903c31346c109a5d0f8bb8a9b37c4723054444a"
IG_USERNAME      = "amerele32"
IG_PASSWORD      = "Eplindefete1@"

MARKETS = [
    "CS.D.NAS100.MINI.IP",
    "CS.D.SPX.MINI.IP",
    "CS.D.DAX.MINI.IP",
    "CS.D.FTSE.MINI.IP"
]

# Strategy thresholds
ATR_PERIOD               = 14
MOMENTUM_THRESHOLD       = 0.0075
WICK_RATIO               = 2.1
CONFIDENCE_MIN_MOMENTUM  = 85    # raised from 75
CONFIDENCE_MIN_WICK      = 90    # raised from 80

# SMTP (override via env vars for security)
SMTP_HOST            = "smtp.gmail.com"
SMTP_PORT            = 587
SMTP_USER            = "adriangat8@gmail.com"
SMTP_PASS            = "mpylpoaqvprbqtoi"
TRADE_ALERT_EMAIL    = "amerele32@yahoo.com"

LONDON_TZ            = "Europe/London"

# === BANKROLL & RISK PARAMETERS ===
INITIAL_BALANCE      = 500.0     # £500 starting demo balance
RISK_PCT             = 0.01      # risk 1% of balance per trade

# Market metadata: minimum sizes and point values
MARKET_INFO = {
    "CS.D.NAS100.MINI.IP": {"min_size": 0.1, "point_value": 1.0},
    "CS.D.SPX.MINI.IP":    {"min_size": 0.1, "point_value": 0.5},
    "CS.D.DAX.MINI.IP":    {"min_size": 0.1, "point_value": 1.0},
    "CS.D.FTSE.MINI.IP":   {"min_size": 0.1, "point_value": 1.0},
}
