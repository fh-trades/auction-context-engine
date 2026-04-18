def get_bias(profile_type, current_price, profile_data):
    """
    Apply bias logic based on profile type and current price.
    Returns (bias, reasoning).
    """
    vah = profile_data['vah']
    val = profile_data['val']
    poc = profile_data['poc']
    
    p_type = profile_type.lower()
    
    if "balanced" in p_type:
        if current_price > vah:
            return "Bullish", f"Price ({current_price:.2f}) is above VAH ({vah:.2f})"
        elif current_price < val:
            return "Bearish", f"Price ({current_price:.2f}) is below VAL ({val:.2f})"
        else:
            return "Neutral", f"Price ({current_price:.2f}) is holding between VAL and VAH"
            
    elif "top-heavy" in p_type:
        if current_price > vah:
            return "Bullish", f"Price ({current_price:.2f}) is above VAH ({vah:.2f}) - Top-heavy breakout"
        elif current_price < poc:
            return "Bearish", f"Price ({current_price:.2f}) is below POC ({poc:.2f}) - Top-heavy failure"
        else:
            return "Neutral", f"Price ({current_price:.2f}) is holding between POC and VAH"
            
    elif "bottom-heavy" in p_type:
        if current_price > poc:
            return "Bullish", f"Price ({current_price:.2f}) is above POC ({poc:.2f}) - Bottom-heavy recovery"
        elif current_price < val:
            return "Bearish", f"Price ({current_price:.2f}) is below VAL ({val:.2f}) - Bottom-heavy breakout"
        else:
            return "Neutral", f"Price ({current_price:.2f}) is holding between VAL and POC"
            
    elif "double-distribution" in p_type or "triple-distribution" in p_type:
        if "uptrend" in p_type:
            if current_price > vah:
                return "Bullish", "Uptrend continuation"
            else:
                return "Bearish", "Uptrend reversal risk"
        else:
            if current_price > val:
                return "Bullish", "Downtrend recovery"
            else:
                return "Bearish", "Downtrend continuation"
            
    elif "thin profile" in p_type:
        if "uptrend" in p_type:
            if current_price > vah:
                return "Bullish", "Thin uptrend continuation"
            elif current_price < poc:
                return "Bearish", "Thin uptrend failure"
            else:
                return "Neutral", "Thin trend consolidation"
        else:
            if current_price > poc:
                return "Bullish", "Thin downtrend recovery"
            elif current_price < val:
                return "Bearish", "Thin downtrend continuation"
            else:
                return "Neutral", "Thin trend consolidation"
            
    return "Unknown", "Could not determine bias"
