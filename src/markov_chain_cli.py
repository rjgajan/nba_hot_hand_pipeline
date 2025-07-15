import sys
import click
import pandas as pd
from src.markov_chain import build_markov

@click.command()
@click.argument('ppm_csv',    type=click.Path(exists=True))
@click.argument('output_csv', type=click.Path())
@click.option('--column', '-c', default='PPM', show_default=True,
              help="Name of the column in ppm_csv to use")
def cli(ppm_csv, output_csv, column):
    """
    Build & save a Markov‑chain transition matrix from a PPM CSV.
    """
    try:
        df = pd.read_csv(ppm_csv)
    except Exception as e:
        click.echo(f"Error reading {ppm_csv}: {e}", err=True); sys.exit(1)
    if column not in df.columns:
        click.echo(f"Column '{column}' not in {ppm_csv}", err=True); sys.exit(1)

    ppm_series = df[column]
    try:
        tm = build_markov(ppm_series)
        tm.to_csv(output_csv)
    except Exception as e:
        click.echo(f"Error building/writing Markov chain: {e}", err=True); sys.exit(2)

    click.echo(f"Markov chain → {output_csv}")

if __name__ == '__main__':
    cli()