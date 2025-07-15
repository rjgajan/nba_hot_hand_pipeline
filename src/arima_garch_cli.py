#!/usr/bin/env python3
import sys
import click
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model

@click.command()
@click.argument('ppm_csv',      type=click.Path(exists=True))
@click.argument('summary_txt',  type=click.Path())
@click.option('--lags',         default=20, show_default=True,
              help='Maximum number of lags for ACF/PACF plots')
@click.option('--column', '-c', default='PPM', show_default=True,
              help="Name of the column in ppm_csv to use")
def cli(ppm_csv, summary_txt, lags, column):
    """
    1) Load PPM series (column `column`)
    2) ADF test
    3) Plot ACF/PACF → prompt d
    4) Plot ACF/PACF on differenced → prompt p,q
    5) Prompt GARCH P,Q
    6) Fit ARIMA + GARCH
    7) Write summary to summary_txt
    """
    # --- 1) Load ---
    try:
        df = pd.read_csv(ppm_csv)
    except Exception as e:
        click.echo(f"Error reading {ppm_csv}: {e}", err=True); sys.exit(1)
    if column not in df.columns:
        click.echo(f"Column '{column}' not found in {ppm_csv}", err=True); sys.exit(1)
    series = df[column].dropna()
    n = len(series)
    if n < 5:
        click.echo("Series too short (<5 observations) for meaningful ACF/PACF.", err=True)
    click.echo(f"Loaded series of length {n}")

    # --- 2) ADF test ---
    try:
        adf_stat, adf_pval, *_ = adfuller(series)
        click.echo(f"ADF test: statistic={adf_stat:.3f}, p-value={adf_pval:.3f}")
    except Exception as e:
        click.echo(f"ADF test failed: {e}", err=True)

    # Helper to plot if possible
    def safe_plot(x, title):
        nonlocal lags
        clean = x.dropna()
        nlags = min(lags, len(clean)-1)
        if nlags < 1 or clean.var() == 0:
            click.echo(f"Skipping {title}: series too short or zero variance.")
            return
        fig, axes = plt.subplots(2,1, figsize=(8,6))
        plot_acf(clean, lags=nlags, ax=axes[0])
        plot_pacf(clean, lags=nlags, ax=axes[1])
        plt.suptitle(title)
        plt.tight_layout(rect=[0,0,1,0.96])
        plt.show()

    # --- 3) ACF/PACF on raw ---
    safe_plot(series, "ACF/PACF of raw series")
    d = click.prompt("Differencing order d", type=int, default=0)

    # --- 4) ACF/PACF on differenced ---
    diffed = series.diff(d).dropna()
    safe_plot(diffed, f"ACF/PACF of differenced (d={d})")
    p = click.prompt("AR order p", type=int, default=1)
    q = click.prompt("MA order q", type=int, default=1)
    click.echo(f"Selected ARIMA({p},{d},{q})")

    # --- 5) GARCH orders ---
    P = click.prompt("GARCH volatility order p", type=int, default=1)
    Q = click.prompt("GARCH innovation order q", type=int, default=1)
    click.echo(f"Selected GARCH({P},{Q})")

    # --- 6) Fit ARIMA + GARCH ---
    click.echo("Fitting ARIMA ...")
    ar_mod = ARIMA(series, order=(p, d, q)).fit()
    click.echo("Fitting GARCH ...")
    garch_mod = arch_model(ar_mod.resid, mean='Zero', vol='Garch', p=P, q=Q).fit(disp='off')

    # --- 7) Summarize ---
    with open(summary_txt, 'w') as f:
        f.write("=== ARIMA/GARCH Model Summary ===\n\n")
        f.write("[ARIMA Results]\n")
        f.write(ar_mod.summary().as_text())
        f.write("\n\n[GARCH Results]\n")
        f.write(garch_mod.summary().as_text())

    click.echo(f"Wrote model summary → {summary_txt}")

if __name__ == '__main__':
    cli()