import pandas as pd
import psycopg2
from pandarallel import pandarallel
import uuid
import logging
from tqdm import tqdm

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pandarallel.initialize(progress_bar=False, verbose=0)

def PGNtoDataFrame(file: str) -> pd.DataFrame:
    """
    Convert a PGN file to a DataFrame.
    :param: file: Path to the PGN file.
    :return: DataFrame containing raw PGN information.
    """
    try:
        logger.info(f"Starting to process PGN file: {file}")
        games = []
        dic = {}

        with open(file, "r") as f:
            for line in f:
                if line.startswith("["):
                    try:
                        header, value = line[1:-2].split(" ", 1)
                        dic[header] = value.strip('"')
                    except ValueError as e:
                        logger.error(f"Error parsing header line: {line.strip()} - {e}")
                elif line.startswith("1") and dic:
                    games.append(dic)
                    dic = {}

        logger.info(f"Finished processing PGN file. Total games: {len(games)}")
        return pd.DataFrame(games)

    except FileNotFoundError as e:
        logger.error(f"File not found: {file} - {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error while processing PGN file: {e}")
        return pd.DataFrame()

def createPlayersDataFrame(gameInfo: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of players from the raw PGN DataFrame.
    :param: gameInfo: DataFrame containing raw PGN information.
    :return: DataFrame containing player information.
    """
    try:
        logger.info("Starting to create players DataFrame")

        if gameInfo.empty:
            logger.warning("Game information DataFrame is empty. Returning an empty players DataFrame.")
            return pd.DataFrame()

        names = pd.melt(gameInfo, value_vars=["White", "Black"], var_name="Color", value_name="name")
        titles = pd.melt(gameInfo, value_vars=["WhiteTitle", "BlackTitle"], var_name="Color", value_name="title")
        players = pd.DataFrame({"name": names["name"], "title": titles["title"]})
        players = players.drop_duplicates(subset=["name"]).reset_index(drop=True)

        players["id"] = [str(uuid.uuid4()) for _ in range(len(players))]

        player_elo = pd.concat([
            gameInfo[["White", "WhiteElo"]].rename(columns={"White": "name", "WhiteElo": "max_elo"}),
            gameInfo[["Black", "BlackElo"]].rename(columns={"Black": "name", "BlackElo": "max_elo"})
        ])
        max_elo_table = player_elo.groupby("name", as_index=False).agg({"max_elo": "max"})
        players = pd.merge(players, max_elo_table, on="name", how="left")

        logger.info(f"Finished creating players DataFrame. Total players: {len(players)}")
        return players

    except KeyError as e:
        logger.error(f"Missing expected column in gameInfo DataFrame: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error while creating players DataFrame: {e}")
        return pd.DataFrame()

def createGamesDataFrame(gameInfo: pd.DataFrame, players: pd.DataFrame, openings: pd.DataFrame) -> pd.DataFrame:
    """
    Create a DataFrame of games from the raw PGN DataFrame.
    :param: gameInfo: DataFrame containing raw PGN information.
    :param: players: DataFrame containing player information.
    :param: openings: DataFrame containing opening information.
    :return: DataFrame containing game information.
    """
    try:
        logger.info("Starting to create games DataFrame")

        if gameInfo.empty or players.empty or openings.empty:
            logger.warning("One or more input DataFrames are empty. Returning an empty games DataFrame.")
            return pd.DataFrame()

        games = pd.DataFrame(columns=["id", "white", "black", "result", "white_elo", "black_elo", "date_time", "time_control", "opening"], index=[])

        games["id"] = [str(uuid.uuid4()) for _ in range(len(gameInfo))]

        player_id_map = players.set_index("name")["id"].to_dict()
        games["white"] = gameInfo["White"].parallel_map(player_id_map)
        games["black"] = gameInfo["Black"].parallel_map(player_id_map)

        games["result"] = gameInfo.parallel_apply(
            lambda row: "D" if row["Result"] == "1/2-1/2" else
                        "W" if row["Result"] == "1-0" else
                        "B" if row["Result"] == "0-1" else
                        None,
            axis=1
        )

        games["white_elo"] = gameInfo["WhiteElo"]
        games["black_elo"] = gameInfo["BlackElo"]
        games["date_time"] = gameInfo["UTCDate"].astype(str) + " " + gameInfo["UTCTime"].astype(str)
        games["time_control"] = gameInfo["TimeControl"]

        opening_id_map = openings.set_index("name")["id"].to_dict()
        games["opening"] = gameInfo["Opening"].parallel_map(lambda x: opening_id_map.get(x, opening_id_map.get(x.split(":")[0])))

        logger.info(f"Finished creating games DataFrame. Total games: {len(games)}")
        return games

    except KeyError as e:
        logger.error(f"Missing expected column in input DataFrames: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error while creating games DataFrame: {e}")
        return pd.DataFrame()

def createOpeningsDataFrame(openingFiles: list[str]) -> pd.DataFrame:
    """
    Create a DataFrame of openings from the lichess opening database's TSV files.
    :param: openingFiles: List of paths to TSV files containing opening information.
    :return: DataFrame containing opening information.
    """
    try:
        logger.info("Starting to create openings DataFrame")
        openings = []

        for openingFile in openingFiles:
            try:
                logger.info(f"Processing opening file: {openingFile}")
                with open(openingFile, "r") as f:
                    AtoE = pd.read_csv(f, sep="\t", header=0, names=["eco", "name", "pgn"])
                    openings.append(AtoE)
            except FileNotFoundError as e:
                logger.error(f"Opening file not found: {openingFile} - {e}")

        openingsDataFrame = pd.concat(openings, ignore_index=True)
        openingsDataFrame["id"] = [str(uuid.uuid4()) for _ in range(len(openingsDataFrame))]

        logger.info(f"Finished creating openings DataFrame. Total openings: {len(openingsDataFrame)}")
        return openingsDataFrame
    except Exception as e:
        logger.error(f"Unexpected error while creating players DataFrame: {e}")
        return pd.DataFrame()

def insertDataToPostgres(connection : psycopg2.extensions.connection, table_name : str, dataframe : pd.DataFrame, chunk_size: int = 1000):
    """
    Insert data from a pandas DataFrame into the PostgreSQL table.
    :param connection: PostgreSQL database connection.
    :param table_name: Name of the table to insert data into.
    :param dataframe: DataFrame containing the data to be inserted.
    :param chunk_size: Number of rows to insert at a time.
    """
    logger.info(f"Starting data insertion into table '{table_name}'.")
    try:
        with connection.cursor() as cursor:
            # Generate the SQL query for batch insertion
            columns = ', '.join(dataframe.columns)
            values = ', '.join(['%s'] * len(dataframe.columns))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING "

            # Convert DataFrame to a list of tuples for batch insertion
            data = [tuple(row) for row in dataframe.itertuples(index=False)]

            # Process data in chunks
            for i in tqdm(range(0, len(data), chunk_size), desc="Inserting rows"):
                chunk = data[i:i + chunk_size]
                cursor.executemany(insert_query, chunk)

            connection.commit()

        logger.info(f"Data insertion completed for table '{table_name}'. Total rows inserted: {len(dataframe)}.")
    except Exception as e:
        logger.error(f"Error during data insertion into table '{table_name}': {e}")
        connection.rollback()