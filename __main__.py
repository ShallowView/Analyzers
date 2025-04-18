import pandas as pd

from CSVtoData import createPlayersDataFrame
from CSVtoData import createGamesDataFrame
from PGNtoCSV import process_pgn

PGNFile = "lichess_elite_2020-06.pgn"
PlayersCSV = "lichess_elite_2020-06_players.csv"
GamesCSV = "lichess_elite_2020-06_games.csv"

process_pgn(PGNFile, "brut.csv")

gameInfo = pd.read_csv("brut.csv")

players = createPlayersDataFrame(gameInfo)

players.to_csv(PlayersCSV, index=False)

games = createGamesDataFrame(gameInfo, players)

games.to_csv("lichess_elite_2020-06_games.csv", index=False)