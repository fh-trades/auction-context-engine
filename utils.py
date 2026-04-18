import pandas as pd
from datetime import datetime, timedelta
import pytz

def get_session_times(target_date: datetime):
    """
    Calculate the prior session's start and end times based on the current day.
    Sessions are 18:00 (Day-1) to 16:59:59 (Day).
    """
    if not isinstance(target_date, datetime):
        target_date = pd.to_datetime(target_date)
        
    weekday = target_date.weekday() # Monday=0, Sunday=6
    
    if weekday == 0: # Monday
        prior_end_day = target_date - timedelta(days=3)
        prior_start_day = target_date - timedelta(days=4)
    else:
        prior_end_day = target_date - timedelta(days=1)
        prior_start_day = target_date - timedelta(days=2)
        
    eastern = pytz.timezone('US/Eastern')
    start_time = eastern.localize(datetime(prior_start_day.year, prior_start_day.month, prior_start_day.day, 18, 0, 0))
    end_time = eastern.localize(datetime(prior_end_day.year, prior_end_day.month, prior_end_day.day, 16, 59, 59))
    
    return start_time, end_time

def extract_sessions(df: pd.DataFrame):
    """
    Slice a bulk historical dataframe into individual sessions (18:00 - 16:59 EST).
    Returns a list of dataframes, each representing one session.
    """
    if df.empty:
        return []

    # Ensure the index is localized to US/Eastern
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC').tz_convert('US/Eastern')
    else:
        df.index = df.index.tz_convert('US/Eastern')

    # Shift time by 18 hours so that 18:00 Day-1 to 16:59 Day-0 falls on the same 'virtual' day
    # Example: Sunday 18:00 -> Sunday 00:00. Monday 16:55 -> Sunday 22:55.
    virtual_time = df.index - timedelta(hours=18)
    df['session_id'] = virtual_time.date

    # Group by session_id and collect dataframes
    sessions = [group for _, group in df.groupby('session_id') if len(group) > 20] # Min 20 bars to be valid
    
    # Sort by time to ensure sequential order
    sessions.sort(key=lambda x: x.index[0])
    
    return sessions
