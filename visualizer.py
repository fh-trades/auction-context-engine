import matplotlib.pyplot as plt
import numpy as np

def plot_profile(ticker, profile_data, profile_type, current_price, bias, reasoning):
    """
    Visualize the volume profile, levels, and bias logic.
    """
    prices = profile_data['price_bins']
    hist = profile_data['histogram']
    vah = profile_data['vah']
    val = profile_data['val']
    poc = profile_data['poc']
    
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # Plot volume profile (horizontal bars)
    ax.barh(prices, hist, height=(prices[1]-prices[0]), color='gray', alpha=0.5, label='Volume Profile')
    
    # Highlight Value Area
    va_mask = (prices >= val) & (prices <= vah)
    ax.barh(prices[va_mask], hist[va_mask], height=(prices[1]-prices[0]), color='blue', alpha=0.3, label='Value Area (70%)')
    
    # Plot Levels
    ax.axhline(vah, color='green', linestyle='--', linewidth=2, label=f'VAH: {vah:.2f}')
    ax.axhline(poc, color='red', linestyle='-', linewidth=2, label=f'POC: {poc:.2f}')
    ax.axhline(val, color='orange', linestyle='--', linewidth=2, label=f'VAL: {val:.2f}')
    
    # Plot Current Price
    ax.axhline(current_price, color='black', marker='>', markersize=12, label=f'Current Price: {current_price:.2f}')
    
    # Title and Reasoning
    plt.suptitle(f"{ticker} - {profile_type}", fontsize=18, fontweight='bold')
    ax.set_title(f"BIAS: {bias}\n{reasoning}", fontsize=12, color='darkblue', style='italic', pad=20)
    
    ax.set_xlabel('Volume')
    ax.set_ylabel('Price')
    ax.legend(loc='upper right')
    ax.grid(axis='x', linestyle=':', alpha=0.6)
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f"{ticker}_analysis.png")
    print(f"Analysis chart saved as {ticker}_analysis.png")
