import click
from src.find_player_id import find_player_id
import sys

@click.command()
@click.argument("player_name", nargs=1)
def cli(player_name):
    "Lookup NBA player ID by player name."
    try:
        player_id = find_player_id(player_name)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(2)

    click.echo(player_id)

if __name__ == "__main__":
    cli()