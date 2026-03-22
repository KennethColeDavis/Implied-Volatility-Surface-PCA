'''
This script is meant to filter an option chain given as a pandas dataframe 
and to return a filter dataframe that is more manageable for my purposes.
Adapted for Polygon.io snapshot data which returns day.vwap instead of bid/ask.
'''
import numpy as np
import pandas as pd

def filter_option_chain(
    df: pd.DataFrame,
    S: float,
    target_date: str,
    moneyness_low: float = 0.80,
    moneyness_high: float = 1.20,
    min_mid: float = 0.05,
    min_volume: int = 1,
    require_oi_or_vol: bool = True
):
    out = df.copy()

    # Normalize column names from Polygon snapshot format
    col_map = {}
    if "details.strike_price" in out.columns:
        col_map["details.strike_price"] = "strike"
    if "details.contract_type" in out.columns:
        col_map["details.contract_type"] = "option_type"
    if "details.expiration_date" in out.columns:
        col_map["details.expiration_date"] = "expiration_date"
    if "day.vwap" in out.columns:
        col_map["day.vwap"] = "mid"
    if "day.volume" in out.columns:
        col_map["day.volume"] = "volume"
    if "open_interest" in out.columns:
        col_map["open_interest"] = "openInterest"
    out = out.rename(columns=col_map)

    # Filter out: inf, nan, zero prices
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out.dropna(subset=["strike", "mid"])
    out = out[out["mid"] > 0]

    # Filter out: small mid prices
    out = out[out["mid"] >= min_mid]

    # Filter out: non-liquid contracts (OI/Volume)
    if require_oi_or_vol:
        if "openInterest" in out.columns and "volume" in out.columns:
            out = out[(out["openInterest"].fillna(0) > 0) | (out["volume"].fillna(0) >= min_volume)]
        elif "openInterest" in out.columns:
            out = out[out["openInterest"].fillna(0) > 0]
        elif "volume" in out.columns:
            out = out[out["volume"].fillna(0) >= min_volume]

    # Moneyness window around spot
    out["moneyness"] = out["strike"] / S
    out["log_moneyness"] = np.log(out["strike"] / S)
    out = out[(out["moneyness"] >= moneyness_low) & (out["moneyness"] <= moneyness_high)]

    # Compute TTM in years
    out["expiration_date"] = pd.to_datetime(out["expiration_date"])
    out["TTM"] = (out["expiration_date"] - pd.Timestamp(target_date)).dt.days / 365.0

    # Apply TTM bounds (14 days to 1 year)
    out = out[(out["TTM"] >= 14/365) & (out["TTM"] <= 1.0)]

    # Sort with the "best" (closest to ATM) first
    out["atm_dist"] = (out["strike"] - S).abs()
    out = out.sort_values(["atm_dist"]).reset_index(drop=True)

    return out