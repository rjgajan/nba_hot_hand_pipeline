import sys
import click
import pandas as pd
from datetime import datetime
from src.monte_carlo import run_mc

@click.command()
@click.argument('ppm_csv',     type=click.Path(exists=True))
@click.argument('nsim',        type=int)
@click.argument('output_txt',  type=click.Path())
@click.option('--column', '-c', default='PPM', show_default=True, help="Name of the column in the input CSV")
@click.option('--window', '-w', default=3, show_default=True, help="Window size for a hot streak")
@click.option('--threshold', '-t', default=None, type=float, help="Explicit threshold (defaults to 80th percentile)")

def cli(ppm_csv, nsim, output_txt, column, window, threshold):
    """
    Hot-streak Monte Carlo analysis:
    1.) historical count
    2.) bootstrap mean/std
    3.) classic mean/std
    """
    # Load
    try:
        df = pd.read_csv(ppm_csv)
    except Exception as e:
        click.echo(f"Error reading {ppm_csv}: {e}", err=True)
        sys.exit(1)

    if column not in df.columns:
        click.echo(f"Column '{column}' not found in {ppm_csv}.", err=True)
        sys.exit(1)

    series = df[column]

    # Run
    try:
        stats = run_mc(series, nsim, threshold=threshold, window=window)
    except Exception as e:
        click.echo(f"Error during Monte Carlo: {e}", err=True)
        sys.exit(2)

    # Build report
    header = (
        f"Hot‑Streak Analysis\n"
        f"Run date: {datetime.utcnow().date()}\n"
        f"Window: {stats['window']}, Threshold: {stats['threshold']:.2f} PPM\n\n"
    )
    body = (
        f"Historical streaks: {stats['historical']}\n"
        f"Bootstrap mean: {stats['bootstrap_mean']:.2f}, std: {stats['bootstrap_std']:.2f}\n"
        f"Classic   mean: {stats['classic_mean']:.2f}, std: {stats['classic_std']:.2f}\n"
    )
    report = header + body

    click.echo(report)

    # Save
    try:
        with open(output_txt, 'w') as f:
            f.write(report)
    except Exception as e:
        click.echo(f"Error writing report to {output_txt}: {e}", err=True)
        sys.exit(3)

    click.echo(f"Report saved to {output_txt}")

if __name__ == '__main__':
    cli()