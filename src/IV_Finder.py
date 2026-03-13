import numpy as np
from scipy.optimize import brentq

from src.black_scholes import black_scholes_price       # Maybe from .black_scholes?

#############################################################################################################################
#Here we solve for implied volatility (sigma) given a market option price by reverse engineering the Black–Scholes formula.
#############################################################################################################################ß


def implied_volatility(price, S, K, T, r, option_type, sigma_low=.00001, sigma_high=5.0):   # arbitrary bounds for volatility

    # Standardize option type input
    option_type = option_type.lower().strip()

    # Define the root-finding target: BS_price(sigma) - market_price = 0
    def findIV(sigma):
        return black_scholes_price(S, K, T, r, sigma, option_type=option_type) - price

    # Find volatilty by using a root-finding algo 
    try:
        return brentq(findIV, sigma_low, sigma_high, maxiter=500)       #brentq is a root-finding algorithm that combines bisection, secant, and inverse quadratic interpolation methodds
    except ValueError:
        # Means the root was not bracketed in [sigma_low, sigma_high]
        return np.nan
