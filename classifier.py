import numpy as np
from scipy.signal import find_peaks
from scipy.stats import skew

def classify_profile(profile_data, df):
    """
    Classify the volume profile into one of the 8 types.
    """
    hist = profile_data['histogram']
    prices = profile_data['price_bins']
    poc = profile_data['poc']
    vah = profile_data['vah']
    val = profile_data['val']
    
    # Peak detection for multi-distribution
    hist_norm = hist / np.max(hist)
    # Use a higher prominence to ignore negligible nodes (noise)
    peaks, properties = find_peaks(hist_norm, prominence=0.35, distance=5)
    num_peaks = len(peaks)
    
    # Determine trend (Uptrend/Downtrend)
    is_uptrend = df['Close'].iloc[-1] > df['Open'].iloc[0]
    
    # Peakiness ratio (Max volume vs Mean volume)
    peakiness = np.max(hist) / np.mean(hist)
    
    # "Thin Profile" detection: 
    # Either the volume is very flat (low peakiness) 
    # OR there are too many small nodes (scattered)
    if peakiness < 2.5 or num_peaks > 3:
        return f"Thin Profile({'uptrend' if is_uptrend else 'downtrend'})"

    if num_peaks == 3:
        return f"Tripple-distribution({'uptrend' if is_uptrend else 'downtrend'}) profile"
    elif num_peaks == 2:
        return f"Double-distribution({'uptrend' if is_uptrend else 'downtrend'}) Profile"
    
    # Single distribution types: Balanced, Top-heavy, Bottom-heavy
    # Calculate where the Value Area center is relative to the total range
    session_high = np.max(prices)
    session_low = np.min(prices)
    va_center = (vah + val) / 2
    
    if session_high != session_low:
        rel_va_pos = (va_center - session_low) / (session_high - session_low)
    else:
        rel_va_pos = 0.5
        
    if rel_va_pos > 0.65: # Value Area is in the upper part of the range
        return "Top-heavy profile"
    elif rel_va_pos < 0.35: # Value Area is in the lower part of the range
        return "Bottom-heavy profile"
    else:
        return "Balanced Profile"
