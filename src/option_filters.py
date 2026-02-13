'''
This script is meant to filter an option chain given as a pandas dataframe 
and to return a filter dataframe that is more manageable for my purposes.
'''

import numpy as np
import pandas as pd

def filter_option_chain(
    df: pd.DataFrame,
    S: float,
    moneyness_low: float = 0.80,
    moneyness_high: float = 1.20,
    max_spread_pct: float = 0.35,
    min_mid: float = 0.05,
    require_oi_or_vol: bool = True
):
    out = df.copy()

    #Filter out: contracts with negative or positve infinty, nan stikes, bids, or asks, where ask is less than bid, ask <= 0, or bid <= 0
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=["strike", "bid", "ask"])
    out = out[(out["bid"] > 0) & (out["ask"] > 0) & (out["ask"] >= out["bid"])]

    #Filter out: small mid prices
    # This is to remove very cheap options that are likely to have unreliable prices and implied volatilities.
    out["mid"] = 0.5 * (out["bid"] + out["ask"])
    out = out[out["mid"] >= min_mid]

    #Filter out: contracts with wide spreads (relative to mid price)
    out["spread"] = out["ask"] - out["bid"]
    out["spread_pct"] = out["spread"] / out["mid"]
    out = out[out["spread_pct"] <= max_spread_pct]

    # Filter out: non-liquid contracts (OI/Volume)
    if require_oi_or_vol:
        if "openInterest" in out.columns and "volume" in out.columns:
            out = out[(out["openInterest"].fillna(0) > 0) | (out["volume"].fillna(0) > 0)]
        elif "openInterest" in out.columns:
            out = out[out["openInterest"].fillna(0) > 0]
        elif "volume" in out.columns:
            out = out[out["volume"].fillna(0) > 0]

    # Moneyness window around spot
    out["moneyness"] = out["strike"] / S
    out = out[(out["moneyness"] >= moneyness_low) & (out["moneyness"] <= moneyness_high)]

    # Sort with the “best” (closest to ATM) first
    out["atm_dist"] = (out["strike"] - S).abs()
    out = out.sort_values(["atm_dist", "spread_pct"]).reset_index(drop=True)

    return out
