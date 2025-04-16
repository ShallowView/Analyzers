
import CSVtoDatabase
import pandas as pd

from PGNtoData import createPlayersDataFrame
from PGNtoData import createGamesDataFrame

PGNFile = "lichess_elite_2020-06.pgn"

gameInfo = pd.read_csv("lichess_elite_2020-06_game_info.csv")

players = createPlayersDataFrame(gameInfo)

players.to_csv("lichess_elite_2020-06_players.csv", index=False)

games = createGamesDataFrame(gameInfo, players)

games.to_csv("lichess_elite_2020-06_games.csv", index=False)

