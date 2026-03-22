# Implied Volatility Surface PCA

An empirical analysis of implied volatility surface dynamics using Principal Component Analysis (PCA) on SPY options, inspired by Cont & da Fonseca (2002).

## Overview

This project builds a daily implied volatility (IV) surface for SPY options across all 250 trading days in 2025, then applies PCA to identify the principal modes of variation in the surface over time.

The key finding — consistent with Cont & da Fonseca — is that **three principal components explain over 99% of the variance** in the IV surface:
- **PC1 (Level)**: Overall parallel shifts in the surface (~95% of variance)
- **PC2 (Slope)**: Changes in the term structure tilt (~3% of variance)
- **PC3 (Curvature)**: Changes in the smile curvature (~1% of variance)

## Methodology

### Data
- **Underlying**: SPY (SPDR S&P 500 ETF)
- **Source**: Polygon.io Options Starter API
- **Period**: Full 2025 trading year (~250 days)
- **Contracts**: OTM options within moneyness range [0.80, 1.20] and TTM range [14 days, 1 year]

### IV Surface Construction
1. Pull end-of-day option snapshots from Polygon.io
2. Filter contracts by moneyness, TTM, liquidity (volume/OI), and minimum price
3. Calculate implied volatility via Black-Scholes inversion (Brent's method)
4. Smooth onto a fixed 50×50 (log-moneyness, TTM) grid using Nadaraya-Watson kernel estimation

### PCA
- Each daily surface is flattened into a 2,500-element vector
- 250 vectors stacked into a 250×2,500 matrix
- Matrix demeaned and PCA applied via scikit-learn
- PC loadings reshaped back to 50×50 for interpretation

## Repository Structure
```
Implied-Volatility-Surface-PCA/
│
├── notebooks/
│   ├── Final/
│   │   ├── 01_data_pull.ipynb          ← Pull SPY option snapshots from Polygon.io
│   │   ├── 02_iv_surface_builder.ipynb ← Filter, calculate IV, build surfaces
│   │   ├── 03_pca_analysis.ipynb       ← Run PCA on surface matrix
│   │   └── 04_summary.ipynb            ← Visualize and summarize findings
│   │
│   └── learning/
│       ├── 01_BS_and_IV_check.ipynb
│       ├── 02_single_day_IV_surface_yfinance.ipynb
│       ├── 03_yfinance_optionchains_datafamiliarity.ipynb
│       └── 03.5_Polygon_io_familiarity.ipynb
│
├── src/
│   ├── black_scholes.py         ← Black-Scholes pricing model
│   ├── IV_Finder.py             ← IV solver (Brent's method)
│   ├── option_filter_polygon.py ← Option chain filter for Polygon data
│   ├── option_filters.py        ← Option chain filter for yfinance data
│   └── risk_free_rate.py        ← Risk-free rate fetcher (^IRX)
│
├── data/
│   ├── raw/        ← Raw Polygon snapshots (gitignored)
│   ├── processed/  ← Filtered + IV calculated DataFrames (gitignored)
│   └── pca/        ← PCA results (explained variance, mean surface)
│
├── figures/        ← Saved plots (gitignored)
├── .gitignore
├── LICENSE
└── README.md
```

## Setup

### Requirements
```bash
conda create -n quant_env python=3.11
conda activate quant_env
conda install numpy pandas matplotlib scipy scikit-learn plotly yfinance
conda install -c conda-forge pandas-market-calendars
pip install polygon-api-client
```

### API Key
You will need a [Polygon.io](https://polygon.io) Options Starter account ($29/month).

Create a file `src/polygonAPIkey.py` with your key:
```python
polygonAPIkey = "your_api_key_here"
```

This file is gitignored and will never be pushed to GitHub.

### Running the Pipeline
Run the notebooks in order:
1. `notebooks/Final/01_data_pull.ipynb` — pulls all 250 days of option data (~5-10 minutes with unlimited API)
2. `notebooks/Final/02_iv_surface_builder.ipynb` — builds IV surfaces for each day
3. `notebooks/Final/03_pca_analysis.ipynb` — runs PCA
4. `notebooks/Final/04_summary.ipynb` — generates all visualizations

Each notebook has resume logic built in — safe to interrupt and rerun.

## Results

| Component | Variance Explained | Cumulative |
|---|---|---|
| PC1 (Level) | ~95% | ~95% |
| PC2 (Slope) | ~3% | ~98% |
| PC3 (Curvature) | ~1% | ~99% |

PC1 shows strong correlation with VIX, confirming it captures the overall level of market volatility expectations.

## References

Cont, R., & da Fonseca, J. (2002). *Dynamics of implied volatility surfaces*. Quantitative Finance, 2(1), 45-60.

## License

MIT
