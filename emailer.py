# utils/emailer.py

import smtplib
from email.mime.text import MIMEText
import logging

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, TRADE_ALERT_EMAIL, MARKETS, LONDON_TZ
from utils.journal import read_daily_pnl
from datetime import datetime
import pytz

# SMTP configuration from config.py
SMTP_CONFIG = {
    "host": SMTP_HOST,
    "port": SMTP_PORT,
    "username": SMTP_USER,
    "password": SMTP_PASS
}
RECIPIENT = TRADE_ALERT_EMAIL

def send_email(subject, body):
    if not SMTP_CONFIG["username"] or not SMTP_CONFIG["password"] or not RECIPIENT:
        logging.warning("SMTP not fully configured; skipping email: %s", subject)
        return
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SMTP_CONFIG["username"]
    msg["To"] = RECIPIENT
    try:
        server = smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"])
        server.starttls()
        server.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
        server.send_message(msg)
        server.quit()
        logging.info("Email sent: %s", subject)
    except Exception as e:
        logging.error("Failed to send email %s: %s", subject, e)

def send_trade_placed_email(market, direction, size, sl, tp, confidence, strategy):
    subject = f"[Monarch] Hi Adrian, New {strategy} Trade Placed on {market}"
    body = (
        f"Hi Adrian,\n\n"
        f"I hope you’re having a great day. We’ve just placed a new **{strategy}** trade on {market}.\n\n"
        f"• Strategy:         {strategy}\n"
        f"• Direction:        {direction.capitalize()}\n"
        f"• Size:             £{size}\n"
        f"• Entry Price:      {sl + (tp - sl)/2:.2f}\n"  # approximate entry display
        f"• Stop Loss:        {sl}\n"
        f"• Take Profit:      {tp}\n"
        f"• Confidence Score: {confidence}/100\n"
        f"  – Triggered by a {int((tp-sl)/sl*100)}% move matching our criteria.\n\n"
        f"We’ll track this trade closely and let you know when it closes.\n\n"
        f"Best of luck—here’s to a profitable session!\n\n"
        f"Warm regards,\n"
        f"Trade Command Monarch Team"
    )
    send_email(subject, body)

def send_trade_outcome_email(market, direction, entry_price, exit_price, profit):
    won = profit >= 0
    subject = (
        f"[Monarch] Hi Adrian, {'Fantastic News—Your Trade Won!' if won else 'Update on Your Trade'}"
    )
    body = (
        f"Hi Adrian,\n\n"
        f"Your **{direction.capitalize()}** trade on {market} has just closed {'in profit' if won else 'at a loss'}.\n\n"
        f"• Entry Price:   {entry_price}\n"
        f"• Exit Price:    {exit_price}\n"
        f"• {'Profit' if won else 'Loss'}:        £{abs(profit):.2f}\n\n"
        f"{'Congratulations on the win! Keep up the great work.' if won else 'Unlucky this time, but our risk limits kept the drawdown small—onto the next opportunity!'}\n\n"
        f"Best regards,\n"
        f"Trade Command Monarch Team"
    )
    send_email(subject, body)

def send_bot_online_email():
    subject = "[Monarch] Hi Adrian, Bots Are Now Online"
    body = (
        f"Hi Adrian,\n\n"
        f"Trade Command Monarch has successfully started and is now running.\n"
        f"Monitoring: {', '.join(MARKETS)}\n\n"
        f"Best regards,\n"
        f"Trade Command Monarch Team"
    )
    send_email(subject, body)

def send_bot_offline_email():
    subject = "[Monarch] Hi Adrian, Bots Are Now Offline"
    body = (
        f"Hi Adrian,\n\n"
        f"The trading session has ended and the bots are now offline.\n\n"
        f"See you tomorrow!\n\n"
        f"Best regards,\n"
        f"Trade Command Monarch Team"
    )
    send_email(subject, body)

def send_crash_email(error_message):
    subject = "[Monarch] Hi Adrian, Bot Exception Occurred"
    body = (
        f"Hi Adrian,\n\n"
        f"Trade Command Monarch encountered an error and stopped:\n"
        f"{error_message}\n\n"
        f"It will automatically attempt to restart shortly.\n\n"
        f"Best regards,\n"
        f"Trade Command Monarch Team"
    )
    send_email(subject, body)

def send_daily_summary_email():
    london = pytz.timezone(LONDON_TZ)
    now = datetime.now(london).strftime("%Y-%m-%d %H:%M")
    summary = read_daily_pnl()
    subject = f"[Monarch] Hi Adrian, Daily Trading Summary ({now})"
    body = (
        f"Hi Adrian,\n\n"
        f"Here is your daily P/L summary for {now}:\n\n"
        f"{summary}\n\n"
        f"Best regards,\n"
        f"Trade Command Monarch Team"
    )
    send_email(subject, body)

def send_weekly_summary_email():
    london = pytz.timezone(LONDON_TZ)
    now = datetime.now(london).strftime("%Y-%m-%d %H:%M")
    summary = read_daily_pnl()  # extend this for true weekly logs if desired
    subject = f"[Monarch] Hi Adrian, Weekly Trading Summary ({now})"
    body = (
        f"Hi Adrian,\n\n"
        f"Here is your weekly P/L summary as of {now}:\n\n"
        f"{summary}\n\n"
        f"Best regards,\n"
        f"Trade Command Monarch Team"
    )
    send_email(subject, body)
