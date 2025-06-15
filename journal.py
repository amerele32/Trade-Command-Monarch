# utils/journal.py
import csv
from datetime import datetime

LOG_FILE = "trade_command_pro_log.csv"

def log_trade(market,direction,sl,tp,confidence,strategy):
    with open(LOG_FILE,'a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(),market,direction,sl,tp,confidence,strategy])

def trade_has_closed(deal_ref):
    return True

def get_trade_details(deal_ref):
    return ("NAS100","LONG",1000.0,1010.0,50.0)

def read_daily_pnl():
    return "Daily P/L summary not implemented."
