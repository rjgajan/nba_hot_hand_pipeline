# NBA Hot‑Hand Pipeline Guide

A self‑contained guide to running our PPM→ARIMA+GARCH→Markov‑chain pipeline, with step‑by‑step instructions and tips for interpreting each output.

---

## Introduction

This pipeline automates the process of:
1. Fetching a player’s Points‑Per‑Minute (PPM) time series.
2. Simulating random scenarios (Monte Carlo).
3. Modeling the PPM series with ARIMA (mean) and GARCH (volatility).
4. Discretizing performance into “hot,” “typical,” and “cold” states and building a Markov transition matrix.

You’ll end up with:
- A PPM CSV
- A Monte Carlo summary  
- An ARIMA+GARCH fit summary
- A 3×3 Markov transition matrix

---

## Prerequisites

- Python 3.8+  
- Make
    - macOS/Linux: should already be installed, check by running `make --version`. Otherwise run `xcode-select --install`
    - Windows: use PowerShell or CMD inside WSL (Ubuntu), or install a standalone Make binary with `choco install make`

---

## Installations

- Clone the repo and enter its folder:
    - `git clone https://github.com/rjgajan/nba_hot_hand_pipeline.git`
    - `cd nba_hot_hand_pipeline`
- Create virtual environment (optional but recommended):
    - `python3 -m venv .venv`
        - macOS: `source .venv/bin/activate`
        - Windows: `.venv\Scripts\Activate.ps1`
- Install dependencies:
    - `pip install --upgrade pip`
    - `pip install -r requirements.txt`

---

## Commands

- make fetchppm: Prompts for a player and seasons, retrieves the player’s ID, and downloads their game‐by‐game PPM into runs/<Player>_<Seasons>/ppm_series.csv (plus a metadata.txt).
- make mc: Runs a Monte Carlo simulation (default 1000 trials) on the PPM series and writes summary statistics (mean, variance, percentiles) to runs/.../monte_carlo.txt.
- make model: make model: Launches an interactive CLI that walks you through stationarity tests, ACF/PACF diagnostics for ARIMA and ARCH tests for GARCH, fits the chosen ARIMA(p,d,q)+GARCH(P,Q) model, and writes a full summary to runs/.../arima_garch_summary.txt.***
- make markov: Reads ppm_series.csv, labels each game as hot (≥ 80th percentile), typical (middle 60%), or cold (≤ 20th percentile), builds a 3×3 row‑stochastic transition matrix, and saves it to runs/.../markov_matrix.csv.
- make all; Runs the entire pipeline.

***Order Selection for ARIMA (p, d, q) and GARCH (p, q)
By default the pipeline suggests ARIMA(1,1,1) and GARCH(1,1), but you should tailor these to your data:

Differencing order (d): plot the ACF of the raw PPM series—if the ACF decays slowly over many lags, set d=1; if it cuts off sharply after one or two lags, d=0; only consider d=2 if the first‐difference still shows slow decay (watch out for a large negative spike at lag 1, which signals over‐differencing).
AR order (p): examine the PACF of your (differenced) series—if the PACF cuts off after lag k, choose p=k; if there’s no clear cutoff, p=1 is a safe starting point.
MA order (q): examine the ACF of the (differenced) series—if the ACF cuts off after lag k, choose q=k; absent a clear cutoff, q=1 works well.
ARCH/GARCH orders (P, Q): on your ARIMA residuals, run an ARCH‑LM test to ensure at least one ARCH term (P≥1 if significant), then plot the ACF of squared residuals—if it cuts off after lag k, set P=k; if it tails off slowly, include a GARCH term (Q≥1). A grid search over P,Q ∈ {1,2} using AIC/BIC can then fine‐tune these defaults, and you should verify that ∑α + ∑β < 1 for stationarity.

---

## Results

- Monte Carlo:
    - A "hot-streak" is defined as 3 consecutive games with an average points per minute at or exceeding the 80th percentile of points per minute from the sample. The number of hot-streak instances from the sample is listed, as well as mean and standard deviation results from both the classic and bootstrap Monte Carlo simulations.

- ARIMA & GARCH:
    - Ljung–Box Q‑statistic: you want p‑values > 0.05 at several lags—if you see p < 0.05, your model hasn’t captured all autocorrelation, so revisit your values for p, d, q.
    - ARCH (α) + GARCH (β) coefficients: check that α + β < 1 (for volatility stationarity). If they sum close to 1, forecasts may be overly persistent.
    - Jarque–Bera test: value less than 5.99 suggests roughly normal residuals. If JB > 5.99 (non‑normal), down‑weight reliance on the simulated Monte Carlo distribution, and consider:
        - refitting GARCH with a heavier‑tailed error (Student‑t or skew‑t),
        - restricting your PPM series to seasons with more consistent contexts (same team/role, no major injuries) to reduce non‑normal shocks.

- Markov Transition Matrix:
    - Historical data is categorized into "hot" (top 20% ppm), "typical" (middle 60% ppm), and "cold" (bottom 20% ppm).
    - Diagonal probabilities (“hot→hot”, “typical→typical”, “cold→cold”): high values indicate strong persistence in a given state (streakiness).
    - Off‑diagonal probabilities quantify how likely performance is to revert or switch states (e.g. “cold→hot” measures bounce‑back chance). Use these to assess momentum or mean‑reversion tendencies in a player’s game‑by‑game efficiency.
    - Note how hot -> cold and cold -> hot probabilities can signify volatility in scoring.