import multiprocessing

import pandas as pd
import psycopg2
from pandarallel import pandarallel
import uuid
import logging
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

pandarallel.initialize(progress_bar=False, verbose=0)

MAX_CORES = multiprocessing.cpu_count() - 1

def setMaxCores(cores: int = multiprocessing.cpu_count() - 1):
    """
    Set the maximum number of cores to be used for parallel processing.
    :param cores: Number of cores to be used.
    """
    global MAX_CORES
    if cores > 0:
        MAX_CORES = cores
        logger.info(f"Max cores set to {MAX_CORES}")
    else:
        logger.warning("Invalid core count. Using default value.")

def __process_pgn_file(file):
    """
    Process a single PGN file and return a DataFrame of games.
    :param file: Path to the PGN file.
    :return: DataFrame containing games from the PGN file.
    """
    try:
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
        return pd.DataFrame(games)
    except FileNotFoundError as e:
        logger.error(f"File not found: {file} - {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error while processing PGN file {file}: {e}")
        return pd.DataFrame()

def PGNtoDataFrame(files: list[str]) -> pd.DataFrame:
    """
    Convert a PGN file to a DataFrame.
    :param: files: list of paths to the PGN files.
    :return: DataFrame containing raw PGN information.
    """
    if not files:
        logger.warning("No PGN files provided. Returning an empty DataFrame.")
        return pd.DataFrame()

    try:
        # Process files in parallel
        with ProcessPoolExecutor(max_workers=MAX_CORES) as executor:
            allGames = list(tqdm(executor.map(__process_pgn_file, files), total=len(files), desc="Processing pgn files"))

        gameInfo = pd.concat(allGames, ignore_index=True)
        logger.info(f"Total games processed: {len(gameInfo)}")
        return gameInfo

    except FileNotFoundError as e:
        logger.error(f"File not found: {file} - {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error while processing PGN file: {e}")
        return pd.DataFrame()

def __process_players_chunk(chunk):
    """
    Process a chunk of the gameInfo DataFrame to extract player information.
    :param chunk: Chunk of the gameInfo DataFrame.
    :return: DataFrame containing player information for the chunk.
    """
    names = pd.melt(chunk, value_vars=["White", "Black"], var_name="Color", value_name="name")
    titles = pd.melt(chunk, value_vars=["WhiteTitle", "BlackTitle"], var_name="Color", value_name="title")
    players = pd.DataFrame({"name": names["name"], "title": titles["title"]})
    players = players.drop_duplicates(subset=["name"]).reset_index(drop=True)

    player_elo = pd.concat([
        chunk[["White", "WhiteElo"]].rename(columns={"White": "name", "WhiteElo": "max_elo"}),
        chunk[["Black", "BlackElo"]].rename(columns={"Black": "name", "BlackElo": "max_elo"})
    ])
    max_elo_table = player_elo.groupby("name", as_index=False).agg({"max_elo": "max"})
    players = pd.merge(players, max_elo_table, on="name", how="left")

    players["id"] = [str(uuid.uuid4()) for _ in range(len(players))]
    return players

def createPlayersDataFrame(gameInfo: pd.DataFrame, chunk_size: int = 10000) -> pd.DataFrame:
    """
    Create a DataFrame of players from the raw PGN DataFrame using multiprocessing.
    :param gameInfo: DataFrame containing raw PGN information.
    :param chunk_size: Number of rows to process at a time.
    :return: DataFrame containing player information.
    """
    try:
        logger.info("Starting to create players DataFrame")

        if gameInfo.empty:
            logger.warning("Game information DataFrame is empty. Returning an empty players DataFrame.")
            return pd.DataFrame()

        # Split gameInfo into chunks
        chunks = [gameInfo.iloc[start:start + chunk_size].copy().reset_index(drop=True)
                  for start in range(0, len(gameInfo), chunk_size)]

        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=MAX_CORES) as executor:
            players_chunks = list(tqdm(executor.map(__process_players_chunk, chunks),
                                       total=len(chunks), desc="Processing player chunks"))

        # Combine all chunks into a single DataFrame
        players = pd.concat(players_chunks, ignore_index=True).drop_duplicates(subset=["name"]).reset_index(drop=True)

        logger.info(f"Finished creating players DataFrame. Total players: {len(players)}")
        return players

    except Exception as e:
        logger.error(f"Unexpected error while creating players DataFrame: {e}")
        return pd.DataFrame()

def __process_games(infoChunk, player_id_map, opening_id_map):
    """
    Process a single chunk of the gameInfo DataFrame.
    :param infoChunk: Chunk of the gameInfo DataFrame.
    :param player_id_map: Dictionary mapping player names to IDs.
    :param opening_id_map: Dictionary mapping opening names to IDs.
    :return: Processed chunk as a DataFrame.
    """
    gameChunk = pd.DataFrame()
    gameChunk["id"] = [str(uuid.uuid4()) for _ in range(len(infoChunk))]
    gameChunk["white"] = infoChunk["White"].map(player_id_map)
    gameChunk["black"] = infoChunk["Black"].map(player_id_map)
    gameChunk["opening"] = infoChunk["Opening"].map(lambda x: opening_id_map.get(x, opening_id_map.get(x.split(":")[0])))
    gameChunk["result"] = infoChunk.apply(
        lambda row: "D" if row["Result"] == "1/2-1/2" else
        "W" if row["Result"] == "1-0" else
        "B" if row["Result"] == "0-1" else
        None,
        axis=1
    )
    gameChunk["white_elo"] = infoChunk["WhiteElo"]
    gameChunk["black_elo"] = infoChunk["BlackElo"]
    gameChunk["date_time"] = infoChunk["UTCDate"].astype(str) + " " + infoChunk["UTCTime"].astype(str)
    gameChunk["time_control"] = infoChunk["TimeControl"]
    return gameChunk

def createGamesDataFrame(gameInfo: pd.DataFrame, players: pd.DataFrame, openings: pd.DataFrame, chunk_size: int = 10000) -> pd.DataFrame:
    """
    Create a DataFrame of games from the raw PGN DataFrame.
    :param gameInfo: DataFrame containing raw PGN information.
    :param players: DataFrame containing player names and IDs from the PostgreSQL database. (must be up to date)
    :param openings: DataFrame containing opening names and IDs from the PostgreSQL database. (must be up to date)
    :param chunk_size: Number of rows to process at a time.
    :return: DataFrame containing game information.
    """
    try:
        logger.info("Starting to create games DataFrame")

        # Check for empty DataFrames
        if gameInfo.empty or players.empty or openings.empty:
            logger.warning("One or more input DataFrames are empty. Returning an empty games DataFrame.")
            return pd.DataFrame()

        # Check for required columns
        required_columns = ["White", "Black", "Result", "WhiteElo", "BlackElo", "UTCDate", "UTCTime", "TimeControl", "Opening"]
        for col in required_columns:
            if col not in gameInfo.columns:
                logger.error(f"Missing required column in gameInfo DataFrame: {col}")
                return pd.DataFrame()

        # Create mapping dictionaries
        player_id_map = players.set_index("name")["id"].to_dict()
        opening_id_map = openings.set_index("name")["id"].to_dict()

        # Split gameInfo into chunks
        chunks = [gameInfo.iloc[start:start + chunk_size].copy().reset_index(drop=True)
                  for start in range(0, len(gameInfo), chunk_size)]

        # Process chunks in parallel
        with ProcessPoolExecutor(max_workers=MAX_CORES) as executor:
            games_chunks = (list(tqdm(executor.map(__process_games, chunks, [player_id_map] * len(chunks), [opening_id_map] * len(chunks)),
                                      total=len(chunks), desc="Processing chunks")))

        games = pd.concat(games_chunks, ignore_index=True)

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

def __insert_chunk_to_postgres(chunk : pd.DataFrame, connection_params : dict, table_name : str):
    """
    Insert a chunk of data into the PostgreSQL table.
    :param chunk: Data chunk to insert.
    :param connection_params: Dictionary of database connection parameters.
    :param table_name: Name of the table to insert data into.
    """
    try:
        connection = psycopg2.connect(**connection_params)
        with connection.cursor() as cursor:
            # Prepare insert query
            columns = ', '.join(chunk.columns)
            values = ', '.join(['%s'] * len(chunk.columns))
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
            # Execute the insert query
            cursor.executemany(insert_query, [tuple(row) for row in chunk.itertuples(index=False)])
        # Commit the transaction
        connection.commit()
        connection.close()
    except Exception as e:
        logging.error(f"Error inserting chunk into table '{table_name}': {e}")

def insertDataToPostgres(connection_params : dict, table_name : str, dataframe : pd.DataFrame, chunk_size: int = 1000):
    """
    Insert data from a pandas DataFrame into the PostgreSQL table.
    :param connection_params: Dictionary of database connection parameters.
    :param table_name: Name of the table to insert data into.
    :param dataframe: DataFrame containing the data to be inserted.
    :param chunk_size: Number of rows to insert at a time.
    """
    logger.info(f"Starting data insertion into table '{table_name}'.")
    try:
        # Split DataFrame into chunks
        chunks = [dataframe.iloc[i:i + chunk_size] for i in range(0, len(dataframe), chunk_size)]

        # Use multiprocessing to insert chunks
        with ProcessPoolExecutor(max_workers=MAX_CORES) as executor:
            list(tqdm(executor.map(__insert_chunk_to_postgres, chunks, [connection_params] * len(chunks), [table_name] * len(chunks)),
                      total=len(chunks), desc="Inserting chunks"))

        logger.info(f"Data insertion completed for table '{table_name}'. Total rows inserted: {len(dataframe)}.")
    except Exception as e:
        logger.error(f"Error during data insertion into table '{table_name}': {e}")