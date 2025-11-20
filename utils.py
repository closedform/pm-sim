import numpy as np

def calculate_sharpe(returns):
    if not returns:
        return 0.0
    return np.mean(returns) / np.std(returns) * np.sqrt(52)

def generate_market_return(regime):
    # Simple regime-based market return generation
    if regime == "Trendy":
        return np.random.normal(0.002, 0.01) # Positive drift
    elif regime == "MeanReverting":
        return np.random.normal(0.0, 0.015) # Higher vol, no drift
    elif regime == "HighVol":
        return np.random.normal(-0.001, 0.03) # Negative drift, high vol
    elif regime == "LowVol":
        return np.random.normal(0.001, 0.005) # Low vol
    else:
        return np.random.normal(0.0, 0.01)

def simulate_alpha_return(alpha, regime):
    # Simulate return for a single alpha
    # Adjust based on regime preference (simplified)
    base_ret = alpha.current_expected_return / 52.0
    vol = alpha.volatility / np.sqrt(52.0)
    
    # Regime penalty/bonus
    if regime == "Trendy" and alpha.style == "Trend":
        base_ret *= 1.2
    elif regime == "MeanReverting" and alpha.style == "Trend":
        base_ret *= 0.5
    
    return np.random.normal(base_ret, vol)
