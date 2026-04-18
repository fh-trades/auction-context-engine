import pandas as pd
from datetime import datetime, timedelta
import pytz

def get_session_times(target_date: datetime):
    """
    Calculate the prior session's start and end times based on the current day.
    Sessions are 18:00 (Day-1) to 16:59:59 (Day).
    
    Monday's prior session is Thursday 18:00 to Friday 17:00.
    """
    # Ensure target_date is a datetime object
    if not isinstance(target_date, datetime):
        target_date = pd.to_datetime(target_date)
        
    weekday = target_date.weekday() # Monday=0, Sunday=6
    
    # Logic for prior session end (The day the session ends)
    if weekday == 0: # Monday
        # Prior is Friday
        prior_end_day = target_date - timedelta(days=3)
        prior_start_day = target_date - timedelta(days=4)
    else:
        # Prior is previous day
        prior_end_day = target_date - timedelta(days=1)
        prior_start_day = target_date - timedelta(days=2)
        
    # Standard Session: 18:00 (Start Day) to 16:59:59 (End Day)
    # We use US/Eastern for futures markets (CME)
    eastern = pytz.timezone('US/Eastern')
    
    start_time = eastern.localize(datetime(prior_start_day.year, prior_start_day.month, prior_start_day.day, 18, 0, 0))
    end_time = eastern.localize(datetime(prior_end_day.year, prior_end_day.month, prior_end_day.day, 16, 59, 59))
    
    return start_time, end_time

def get_current_day_start(target_date: datetime):
    """
    Get the start of the current session (18:00 previous day).
    """
    eastern = pytz.timezone('US/Eastern')
    # If today is Monday, session started Sunday 18:00
    # If today is Tuesday-Friday, session started yesterday 18:00
    weekday = target_date.weekday()
    
    if weekday == 0: # Monday
        start_day = target_date - timedelta(days=1) # Sunday
    else:
        start_day = target_date - timedelta(days=1)
        
    return eastern.localize(datetime(start_day.year, start_day.month, start_day.day, 18, 0, 0))
