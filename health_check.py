# utils/health_check.py

import time
import json
from utils.stream_fetcher import start_streaming
from utils.filters import momentum_logic_passed, wick_rejection_logic_passed, trend_continuation_logic_passed

# Initialize global variable for the confidence threshold
CONFIDENCE_THRESHOLD = 85  # Default confidence for trades

def check_health():
    """
    Checks the health of the system (e.g., if bots are alive).
    """
    print("Checking system health...")

def get_confidence_threshold():
    """
    Fetch the current global confidence threshold from a persistent storage or config.
    """
    global CONFIDENCE_THRESHOLD
    return CONFIDENCE_THRESHOLD

def set_confidence_threshold(value):
    """
    Set the global confidence threshold for bots.
    """
    global CONFIDENCE_THRESHOLD
    CONFIDENCE_THRESHOLD = value

def record_bot_heartbeat(bot_name):
    """
    Record heartbeat for each bot (used for monitoring).
    """
    print(f"❤️ {bot_name} heartbeat recorded!")

def update_confidence_threshold(new_threshold):
    """
    Update the confidence threshold in the system.
    """
    set_confidence_threshold(new_threshold)
    print(f"✅ Updated confidence threshold to {new_threshold}")
