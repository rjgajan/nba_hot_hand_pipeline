import sys
import click
import pandas as pd
from src.get_ppm import points_per_min

@click.command()
@click.option(
    '--player-name', '-n',
    required=True,
    help="Full name of the player (for CSV metadata)"
)
@click.argument('player_id',       type=int)
@click.argument('output_csv',      type=click.Path())
@click.argument('metadata_output', type=click.Path())
@click.argument('seasons', nargs=-1, required=True)
def cli(player_name, player_id, output_csv, metadata_output, seasons):
    """
    Get points‑per‑minute for a player over one or more seasons.
    Writes a CSV with a single column: PPM.
    Also writes a metadata file with player_id, player_name, seasons.
    """
    season_list = list(seasons)
    try:
        ppm_series = points_per_min(player_id, season_list)
    except (TypeError, ValueError) as e:
        click.echo(f"Input error: {e}", err=True); sys.exit(1)
    except RuntimeError as e:
        click.echo(f"Data error: {e}", err=True); sys.exit(2)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True); sys.exit(3)

    # Build a DataFrame with only the PPM column
    df = pd.DataFrame({'PPM': ppm_series})

    try:
        df.to_csv(output_csv, index=False)
    except Exception as e:
        click.echo(f"Error writing {output_csv}: {e}", err=True); sys.exit(4)

    # Write metadata separately
    try:
        with open(metadata_output, 'w') as f:
            f.write(f"player_id: {player_id}\n")
            f.write(f"player_name: {player_name}\n")
            f.write(f"seasons: {','.join(season_list)}\n")
    except Exception as e:
        click.echo(f"Error writing metadata to {metadata_output}: {e}", err=True)
        sys.exit(5)

    click.echo(f"Wrote PPM series → {output_csv}")
    click.echo(f"Wrote metadata   → {metadata_output}")

if __name__ == '__main__':
    cli()