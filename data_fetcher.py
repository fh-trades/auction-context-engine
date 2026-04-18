import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

def fetch_data(ticker: str, start: datetime, end: datetime, interval: str = '5m'):
    """
    Fetch historical data from Yahoo Finance.
    Note: 1m data is only available for the last 7 days.
    5m data is available for 60 days.
    """
    # yfinance expects strings or datetime objects in UTC usually, but we can pass localized datetimes
    data = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
    
    if data.empty:
        return data
        
    # Standardize column names (sometimes yfinance returns multi-index if many tickers)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    return data

def get_current_price(ticker: str):
    """
    Get the latest price for a ticker.
    """
    tick = yf.Ticker(ticker)
    # Get last close from fast_info or history
    try:
        data = tick.history(period='1d', interval='1m')
        if not data.empty:
            return data['Close'].iloc[-1]
    except:
        pass
    return None

def calculate_atr(df: pd.DataFrame, period: int = 14):
    """
    Calculate ATR from a dataframe.
    """
    if len(df) < period:
        return None
        
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()
    
    return atr.iloc[-1]
