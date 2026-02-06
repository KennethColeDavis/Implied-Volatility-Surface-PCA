#import necessary libraries 
import numpy as np
from scipy.stats import norm

"""
Black Scholes price for a European call or put.
"""

def black_scholes_price(S, K, T, r, sigma, option_type):

    # Standardize option type input
    option_type = option_type.lower().strip()

    #These are all error checks 
    if S <= 0 or K <= 0:
        raise ValueError("Spot and Strike must be positive.")
    if T < 0:
        raise ValueError("Time must be non-negative.")
    if sigma < 0:
        raise ValueError("sigma (Volatility) must be non-negative.")

    # Incase of options being pulled are at maturity
    if T == 0:
        if option_type == "call":
            return max(S - K, 0.0)        #Options are not executed if out of the money
        elif option_type == "put":
            return max(K - S, 0.0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    # Zero volatility case -  This means that the stock price is determinists
    # Very unlikely but handled for completeness (This is being made prior to looking at the data)
    if sigma == 0:
        forward = S * np.exp(r * T)
        if option_type == "call":
            return np.exp(-r * T) * max(forward - K, 0.0)     # -r to translate to present value value
        elif option_type == "put":
            return np.exp(-r * T) * max(K - forward, 0.0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")

    # Classic Black-Scholes formula from here
    sqrtT = np.sqrt(T)
    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT

    if option_type == "call":
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")
