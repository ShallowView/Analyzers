import pandas as pd
from pandarallel import pandarallel
import uuid

pandarallel.initialize(progress_bar=False, verbose=0)

def createPlayersDataFrame(gameInfo: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of players from the game information DataFrame.
    """
    players = pd.melt(gameInfo, value_vars=["White", "Black"], var_name="Color", value_name="PlayerName")
    players = players.drop(columns=["Color"])
    players["Title"] = pd.melt(gameInfo, value_vars=["WhiteTitle", "BlackTitle"], var_name="Color", value_name="Title")["Title"].values
    players.drop_duplicates(["PlayerName"], inplace=True)
    players["id"] = [str(uuid.uuid4()) for _ in range(len(players))]

    # Combine white and black players with their respective Elo ratings
    player_elo = pd.concat([
        gameInfo[["White", "WhiteElo"]].rename(columns={"White": "PlayerName", "WhiteElo": "MaxElo"}),
        gameInfo[["Black", "BlackElo"]].rename(columns={"Black": "PlayerName", "BlackElo": "MaxElo"})
    ])

    # Group by player name and calculate the maximum Elo
    max_elo_table = player_elo.groupby("PlayerName", as_index=False).agg({"MaxElo": "max"})

    # Merge the Elo ratings with the players DataFrame
    players = pd.merge(players, max_elo_table, on="PlayerName", how="left")

    return players

def createGamesDataFrame(gameInfo: pd.DataFrame, players: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of games from the game information DataFrame.
    """
    # Create a DataFrame for the games
    games = pd.DataFrame(columns=["id", "White", "Black", "Result", "WhiteElo", "BlackElo", "Date", "TimeControl", "ECO"], index=[])
    games["id"] = [str(uuid.uuid4()) for _ in range(len(gameInfo))]

    player_id_map = players.set_index("PlayerName")["id"].to_dict()
    games["White"] = gameInfo["White"].parallel_map(player_id_map)
    games["Black"] = gameInfo["Black"].parallel_map(player_id_map)

    # Map the Result column based on the winner
    games["Result"] = gameInfo.parallel_apply(
        lambda row: "D" if row["Result"] == "1/2-1/2" else
                    "W" if row["Result"] == "1-0" else
                    "B" if row["Result"] == "0-1" else
                    None,
        axis=1
    )
    games["WhiteElo"] = gameInfo["WhiteElo"]
    games["BlackElo"] = gameInfo["BlackElo"]
    games["Date"] = gameInfo["UTCDate"]
    games["TimeControl"] = gameInfo["TimeControl"]
    games["ECO"] = gameInfo["ECO"]

    return games