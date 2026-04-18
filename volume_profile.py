import pandas as pd
import numpy as np

def calculate_volume_profile(df: pd.DataFrame, bins: int = 50):
    """
    Calculate Volume Profile (POC, VAH, VAL, and Histogram).
    """
    if df.empty:
        return None

    # Determine price range
    min_price = df['Low'].min()
    max_price = df['High'].max()
    
    # Create price bins
    # We use a bit more than 'bins' to ensure we cover the range nicely
    price_bins = np.linspace(min_price, max_price, bins)
    bin_width = price_bins[1] - price_bins[0]
    
    # Aggregate volume into bins
    # For each row, we distribute volume across the price range [Low, High]
    # Simple approach: assign full volume to the bin containing the 'Close' 
    # Better approach: distribute volume across bins touched by [Low, High]
    
    histogram = np.zeros(len(price_bins))
    
    for _, row in df.iterrows():
        # Find bins touched by this bar
        mask = (price_bins >= row['Low'] - bin_width/2) & (price_bins <= row['High'] + bin_width/2)
        indices = np.where(mask)[0]
        if len(indices) > 0:
            # Distribute volume equally across bins touched
            vol_per_bin = row['Volume'] / len(indices)
            histogram[indices] += vol_per_bin
        else:
            # Fallback to close price
            idx = np.argmin(np.abs(price_bins - row['Close']))
            histogram[idx] += row['Volume']

    # POC: Bin with max volume
    poc_idx = np.argmax(histogram)
    poc = price_bins[poc_idx]
    
    # Value Area (70% of total volume)
    total_volume = np.sum(histogram)
    va_volume_target = total_volume * 0.70
    
    # Start at POC and expand outwards
    low_idx = poc_idx
    high_idx = poc_idx
    current_va_volume = histogram[poc_idx]
    
    while current_va_volume < va_volume_target:
        # Check volume of next bins
        prev_low_vol = histogram[low_idx - 1] if low_idx > 0 else 0
        next_high_vol = histogram[high_idx + 1] if high_idx < len(histogram) - 1 else 0
        
        if prev_low_vol == 0 and next_high_vol == 0:
            break
            
        if prev_low_vol >= next_high_vol:
            current_va_volume += prev_low_vol
            low_idx -= 1
        else:
            current_va_volume += next_high_vol
            high_idx += 1
            
    vah = price_bins[high_idx]
    val = price_bins[low_idx]
    
    return {
        'poc': poc,
        'vah': vah,
        'val': val,
        'histogram': histogram,
        'price_bins': price_bins,
        'total_volume': total_volume,
        'bin_width': bin_width
    }
