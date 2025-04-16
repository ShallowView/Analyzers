import pandas as pd
from pandarallel import pandarallel
from converter.pgn_data import PGNData
import uuid

pandarallel.initialize(progress_bar=False, verbose=0)


def generateCSV(pgn_file: str) -> None:
    """
    Generate a CSV file from the PGN file.
    """
    pgn = PGNData(pgn_file)
    pgn.export(moves_required=False)

def createPlayersDataFrame(gameInfo: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of players from the game information DataFrame.
    """
    players = pd.melt(gameInfo, value_vars=["white", "black"], var_name="Color", value_name="PlayerName")
    players = players.drop(columns=["Color"])
    players["Title"] = pd.melt(gameInfo, value_vars=["white_title", "black_title"], var_name="Color", value_name="Title")["Title"].values
    players.drop_duplicates(["PlayerName"], inplace=True)
    players["id"] = [str(uuid.uuid4()) for _ in range(len(players))]

    # Combine white and black players with their respective Elo ratings
    player_elo = pd.concat([
        gameInfo[["white", "white_elo"]].rename(columns={"white": "PlayerName", "white_elo": "MaxElo"}),
        gameInfo[["black", "black_elo"]].rename(columns={"black": "PlayerName", "black_elo": "MaxElo"})
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
    games["id"] = gameInfo["game_id"]
    player_id_map = players.set_index("PlayerName")["id"].to_dict()
    games["White"] = gameInfo["white"].parallel_map(player_id_map)
    games["Black"] = gameInfo["black"].parallel_map(player_id_map)

    # Map the Result column based on the winner
    games["Result"] = gameInfo.parallel_apply(
        lambda row: "D" if row["winner"] == "draw" else
                    "W" if row["winner"] == row["white"] else
                    "B" if row["winner"] == row["black"] else
                    None,
        axis=1
    )
    games["WhiteElo"] = gameInfo["white_elo"]
    games["BlackElo"] = gameInfo["black_elo"]
    games["Date"] = gameInfo["date_created"]
    games["TimeControl"] = gameInfo["time_control"]
    games["ECO"] = gameInfo["eco"]

    return games