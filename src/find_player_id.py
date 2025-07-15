from nba_api.stats.static import players

def find_player_id(name: str) -> str:
    matches = players.find_players_by_full_name(name)
    if matches:
        player_id = matches[0]['id']
        return player_id
    else:
        raise ValueError(f"No player found matching name: {name!r}")

if __name__ =="__main__":
    print(find_player_id("Lebron James"))