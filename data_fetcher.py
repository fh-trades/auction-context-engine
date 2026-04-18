import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

def fetch_data(ticker: str, start: datetime, end: datetime, interval: str = '5m'):
    """
    Fetch historical data from Yahoo Finance.
    """
    data = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
    
    if data.empty:
        return data
        
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    return data

def get_current_price(ticker: str):
    """
    Get the latest price for a ticker.
    """
    tick = yf.Ticker(ticker)
    try:
        data = tick.history(period='1d', interval='1m')
        if not data.empty:
            return data['Close'].iloc[-1]
    except:
        pass
    return None

def fetch_bulk_data(ticker: str, days: int = 60, interval: str = '5m'):
    """
    Fetch a large block of historical data.
    """
    end = datetime.now()
    start = end - timedelta(days=days)
    
    data = yf.download(ticker, start=start, end=end, interval=interval, progress=True)
    
    if data.empty:
        return data
        
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    return data
