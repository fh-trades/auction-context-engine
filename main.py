import sys
from datetime import datetime
import pytz
from utils import get_session_times
from data_fetcher import fetch_data, get_current_price
from volume_profile import calculate_volume_profile
from classifier import classify_profile
from bias_analyzer import get_bias
from visualizer import plot_profile

def analyze_ticker(ticker):
    print(f"\n--- Analyzing {ticker} ---")
    
    # Use current time in US/Eastern
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # 1. Determine Prior Session
    start_time, end_time = get_session_times(now)
    print(f"Prior Session: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} (EST)")
    
    # 2. Fetch Data
    # Fetch data for the prior session. yfinance works best if we fetch slightly more data
    # to ensure the full session is captured.
    df = fetch_data(ticker, start_time, end_time, interval='5m')
    
    if df.empty:
        print(f"Error: No data found for {ticker} in the specified timeframe.")
        return

    # 3. Calculate Volume Profile
    profile = calculate_volume_profile(df)
    if not profile:
        print("Error: Could not calculate volume profile.")
        return
        
    # 4. Classify Profile
    profile_type = classify_profile(profile, df)
    print(f"Profile Type: {profile_type}")
    print(f"Levels: VAH={profile['vah']:.2f}, POC={profile['poc']:.2f}, VAL={profile['val']:.2f}")
    
    # 5. Get Current Price
    current_price = get_current_price(ticker)
    if current_price is None:
        print("Error: Could not fetch current price.")
        return
    print(f"Current Price: {current_price:.2f}")
    
    # 6. Determine Bias
    bias, reasoning = get_bias(profile_type, current_price, profile)
    print(f"--- BIAS: {bias} ---")
    print(f"Reasoning: {reasoning}")
    
    # 7. Visualize
    plot_profile(ticker, profile, profile_type, current_price, bias, reasoning)

if __name__ == "__main__":
    # Ticker for futures usually ES=F, NQ=F, CL=F, etc.
    ticker = "ES=F"
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    
    analyze_ticker(ticker)
