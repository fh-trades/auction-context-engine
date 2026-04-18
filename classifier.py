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
    
    # 1. Peak detection for multi-distribution
    hist_norm = hist / np.max(hist)
    peaks, properties = find_peaks(hist_norm, prominence=0.35, distance=5)
    num_peaks = len(peaks)
    
    # 2. Determine trend (Uptrend/Downtrend)
    is_uptrend = df['Close'].iloc[-1] > df['Open'].iloc[0]
    
    # 3. Peakiness ratio (Max volume vs Mean volume)
    peakiness = np.max(hist) / np.mean(hist)
    
    # 4. Value Area Positioning (Relative Position)
    session_high = np.max(prices)
    session_low = np.min(prices)
    va_center = (vah + val) / 2
    if session_high != session_low:
        rel_va_pos = (va_center - session_low) / (session_high - session_low)
    else:
        rel_va_pos = 0.5
        
    # Metrics for confidence calculation
    metrics = {
        'peakiness': peakiness,
        'num_peaks': num_peaks,
        'rel_va_pos': rel_va_pos,
        'is_uptrend': is_uptrend
    }

    # 5. Profile Classification Logic
    if peakiness < 2.5 or num_peaks > 3:
        return f"Thin Profile({'uptrend' if is_uptrend else 'downtrend'})", metrics

    if num_peaks == 3:
        return f"Triple-distribution({'uptrend' if is_uptrend else 'downtrend'}) profile", metrics
    elif num_peaks == 2:
        return f"Double-distribution({'uptrend' if is_uptrend else 'downtrend'}) Profile", metrics
    
    # Single distribution types
    if rel_va_pos > 0.65:
        return "Top-heavy profile", metrics
    elif rel_va_pos < 0.35:
        return "Bottom-heavy profile", metrics
    else:
        return "Balanced Profile", metrics
