import math

# --- CONFIGURABLE WEIGHTS ---
W_DISTANCE = 0.50
W_PEAKINESS = 0.30
W_ALIGNMENT = 0.20
# Ensure weights sum to 1.0
TOTAL_W = W_DISTANCE + W_PEAKINESS + W_ALIGNMENT
W_DISTANCE /= TOTAL_W
W_PEAKINESS /= TOTAL_W
W_ALIGNMENT /= TOTAL_W

def sigmoid(x):
    """Smooth probability-like output between 0 and 1."""
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 1.0 if x > 0 else 0.0

def calculate_confidence_v2(bias, current_price, profile_data, metrics, atr):
    """
    Data-driven normalized confidence model.
    """
    if bias == "Neutral" or bias == "Unknown" or atr is None or atr == 0:
        return {
            "confidence": 0.50,
            "components": {"distance": 0.0, "peakiness": 0.0, "alignment": 0.0}
        }

    # 1. Normalized Distance Score (ATR-based)
    # Range: 0 to 3 ATRs. We center it so that being at the level is 0.
    vah = profile_data['vah']
    val = profile_data['val']
    
    raw_dist = 0
    if bias == "Bullish":
        raw_dist = (current_price - vah) / atr
    elif bias == "Bearish":
        raw_dist = (val - current_price) / atr
    
    # Clip and Scale: 0 ATR = 0, 2 ATR = 3.0 (strong conviction)
    # We want this to be a meaningful input to sigmoid
    s_dist = max(0, min(raw_dist, 3.0)) * 1.5 
    
    # 2. Normalized Peakiness Score (Min-Max)
    # Range: 2.5 (Thin) to 10.0 (Very Sharp)
    peakiness = metrics.get('peakiness', 2.5)
    s_peak = (peakiness - 2.5) / (10.0 - 2.5)
    s_peak = max(0, min(s_peak, 1.0)) * 2.0 # Scale to contribute up to 2.0 to sigmoid
    
    # 3. Structural Alignment Score (Binary/Scaled)
    is_uptrend = metrics.get('is_uptrend', True)
    alignment = 0
    if (bias == "Bullish" and is_uptrend) or (bias == "Bearish" and not is_uptrend):
        alignment = 1.0
    
    s_align = alignment * 1.0 # Contribution to sigmoid
    
    # Weighted Score
    # We shift the score so that "Neutral/Starting" is 0
    weighted_score = (W_DISTANCE * s_dist) + (W_PEAKINESS * s_peak) + (W_ALIGNMENT * s_align)
    
    confidence = round(sigmoid(weighted_score), 2)
    
    return {
        "confidence": confidence,
        "components": {
            "distance": round(W_DISTANCE * s_dist, 3),
            "peakiness": round(W_PEAKINESS * s_peak, 3),
            "alignment": round(W_ALIGNMENT * s_align, 3)
        }
    }

def get_bias(profile_type, current_price, profile_data, metrics, atr=None):
    """
    Apply bias logic and return structured confidence data.
    """
    vah = profile_data['vah']
    val = profile_data['val']
    poc = profile_data['poc']
    
    p_type = profile_type.lower()
    bias = "Unknown"
    reasoning = "Could not determine bias"
    
    if "balanced" in p_type:
        if current_price > vah:
            bias, reasoning = "Bullish", f"Price above VAH ({vah:.2f})"
        elif current_price < val:
            bias, reasoning = "Bearish", f"Price below VAL ({val:.2f})"
        else:
            bias, reasoning = "Neutral", "Price holding in balance"
            
    elif "top-heavy" in p_type:
        if current_price > vah:
            bias, reasoning = "Bullish", "Top-heavy breakout"
        elif current_price < poc:
            bias, reasoning = "Bearish", "Top-heavy failure"
        else:
            bias, reasoning = "Neutral", "Holding in upper value"
            
    elif "bottom-heavy" in p_type:
        if current_price > poc:
            bias, reasoning = "Bullish", "Bottom-heavy recovery"
        elif current_price < val:
            bias, reasoning = "Bearish", "Bottom-heavy breakout"
        else:
            bias, reasoning = "Neutral", "Holding in lower value"
            
    elif "double-distribution" in p_type or "triple-distribution" in p_type:
        if "uptrend" in p_type:
            if current_price > vah:
                bias, reasoning = "Bullish", "Uptrend continuation"
            else:
                bias, reasoning = "Bearish", "Uptrend reversal risk"
        else:
            if current_price > val:
                bias, reasoning = "Bullish", "Downtrend recovery"
            else:
                bias, reasoning = "Bearish", "Downtrend continuation"
            
    elif "thin profile" in p_type:
        if "uptrend" in p_type:
            if current_price > vah:
                bias, reasoning = "Bullish", "Thin uptrend continuation"
            elif current_price < poc:
                bias, reasoning = "Bearish", "Thin uptrend failure"
            else:
                bias, reasoning = "Neutral", "Thin trend consolidation"
        else:
            if current_price > poc:
                bias, reasoning = "Bullish", "Thin downtrend recovery"
            elif current_price < val:
                bias, reasoning = "Bearish", "Thin downtrend continuation"
            else:
                bias, reasoning = "Neutral", "Thin trend consolidation"
                
    conf_data = calculate_confidence_v2(bias, current_price, profile_data, metrics, atr)
    return bias, reasoning, conf_data
