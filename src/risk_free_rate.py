# This module will be responsible for calculating the risk free rate to be used in the Black-Scholes model
import yfinance as yf

def calculate_risk_free_rate():
    ticker = "^IRX"  # 13-week Treasury bill for now
    treasury = yf.Ticker(ticker)

    rate_percent = treasury.info["regularMarketPrice"]
    rate_decimal = rate_percent / 100.0

    return rate_decimal

