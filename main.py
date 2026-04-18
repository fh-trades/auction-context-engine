import sys
import os
import csv
from datetime import datetime
import pytz
from utils import get_session_times
from data_fetcher import fetch_data, get_current_price, calculate_atr
from volume_profile import calculate_volume_profile
from classifier import classify_profile
from bias_analyzer import get_bias
from visualizer import plot_profile

def log_results(ticker, timestamp, profile_type, bias, conf_data, current_price):
    """
    Store results for future backtesting.
    """
    log_file = "analysis_history.csv"
    file_exists = os.path.isfile(log_file)
    
    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Ticker', 'ProfileType', 'Bias', 'Confidence', 'DistComp', 'PeakComp', 'AlignComp', 'Price'])
        
        writer.writerow([
            timestamp.strftime('%Y-%m-%d %H:%M'),
            ticker,
            profile_type,
            bias,
            conf_data['confidence'],
            conf_data['components']['distance'],
            conf_data['components']['peakiness'],
            conf_data['components']['alignment'],
            current_price
        ])

def analyze_ticker(ticker):
    print(f"\n--- Analyzing {ticker} ---")
    
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    
    # 1. Determine Prior Session
    start_time, end_time = get_session_times(now)
    print(f"Prior Session: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} (EST)")
    
    # 2. Fetch Data
    df = fetch_data(ticker, start_time, end_time, interval='5m')
    if df.empty:
        print(f"Error: No data found for {ticker}.")
        return

    # 3. Calculate Metrics (Volume Profile + ATR)
    profile = calculate_volume_profile(df)
    atr = calculate_atr(df)
    if not profile or atr is None:
        print("Error: Could not calculate profile or ATR.")
        return
        
    # 4. Classify Profile
    profile_type, metrics = classify_profile(profile, df)
    print(f"Profile Type: {profile_type}")
    print(f"ATR (Volatility): {atr:.2f}")
    
    # 5. Get Current Price
    current_price = get_current_price(ticker)
    if current_price is None:
        print("Error: Could not fetch current price.")
        return
    print(f"Current Price: {current_price:.2f}")
    
    # 6. Determine Bias & Confidence
    bias, reasoning, conf_data = get_bias(profile_type, current_price, profile, metrics, atr)
    
    print(f"--- BIAS: {bias} (Confidence: {conf_data['confidence']}) ---")
    print(f"Components: {conf_data['components']}")
    print(f"Reasoning: {reasoning}")
    
    # 7. Log and Visualize
    log_results(ticker, now, profile_type, bias, conf_data, current_price)
    plot_profile(ticker, profile, profile_type, current_price, bias, reasoning, conf_data['confidence'])

if __name__ == "__main__":
    ticker = "ES=F"
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    
    analyze_ticker(ticker)
