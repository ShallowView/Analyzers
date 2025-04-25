import multiprocessing
import pandas as pd
import psycopg
import uuid
import logging
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAX_CORES = max(multiprocessing.cpu_count()//5*4, multiprocessing.cpu_count()%5 - 1, 1)  # Default to 80% of available cores

global_connection = None

def __connection_initializer(connection_params:dict)->None:
    """
    Initialize a global connection for each process in multiprocessing.
    :param connection_params: Dictionary of database connection parameters.
    """
    global global_connection
    global_connection = psycopg.connect(**connection_params)

def setMaxCores(cores: int = max(multiprocessing.cpu_count()//5*4, multiprocessing.cpu_count()%5 - 1, 1)) -> None:
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

def __process_pgn_file(file : str) -> pd.DataFrame:
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

    except Exception as e:
        logger.error(f"Unexpected error while processing PGN files: {e}")
        return pd.DataFrame()

def __process_players_chunk(chunk : pd.DataFrame, DBPlayers : pd.DataFrame) -> pd.DataFrame:
    """
    Process a chunk of the gameInfo DataFrame to extract player information.
    :param chunk: Chunk of the gameInfo DataFrame.
    :param DBPlayers: DataFrame containing player names and ID from the PostgreSQL database.
    :return: DataFrame containing player information for the chunk.
    """
    names = pd.melt(chunk, value_vars=["White", "Black"], var_name="Color", value_name="name")
    titles = pd.melt(chunk, value_vars=["WhiteTitle", "BlackTitle"], var_name="Color", value_name="title")
    players = pd.DataFrame({"name": names["name"], "title": titles["title"]})

    players = players.drop_duplicates(subset=["name"]).reset_index(drop=True)
    # Filter out players already in the database
    if not DBPlayers.empty:
        players = players[~players["name"].isin(DBPlayers["name"])]

    players["id"] = [str(uuid.uuid4()) for _ in range(len(players))]
    return players

def createPlayersDataFrame(gameInfo: pd.DataFrame, DBPlayers : pd.DataFrame, chunk_size: int = 10000) -> pd.DataFrame:
    """
    Create a DataFrame of players from the raw PGN DataFrame using multiprocessing.
    :param gameInfo: DataFrame containing raw PGN information.
    :param DBPlayers: DataFrame containing player names and ID from the PostgreSQL database.
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
            players_chunks = list(tqdm(executor.map(__process_players_chunk, chunks, [DBPlayers] * len(chunks)),
                                       total=len(chunks), desc="Processing player chunks"))

        # Combine all chunks into a single DataFrame
        players = pd.concat(players_chunks, ignore_index=True).drop_duplicates(subset=["name"]).reset_index(drop=True)

        logger.info(f"Finished creating players DataFrame. Total new players: {len(players)}")
        return players

    except Exception as e:
        logger.error(f"Unexpected error while creating players DataFrame: {e}")
        return pd.DataFrame()

def __process_games(infoChunk : pd.DataFrame, player_id_map : dict, opening_id_map : dict) -> pd.DataFrame:
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

def __insert_chunk_to_postgres(chunk : pd.DataFrame, table_name : str) -> None:
    """
    Insert a chunk of data into the PostgreSQL table.
    :param chunk: Data chunk to insert.
    :param table_name: Name of the table to insert data into.
    """
    global global_connection
    try:
        with global_connection.cursor() as cursor:
            # Prepare the insert query
            insert_query = psycopg.sql.SQL(
                "INSERT INTO {table} ({columns}) VALUES ({values}) ON CONFLICT DO NOTHING"
            ).format(
                table=psycopg.sql.Identifier(table_name),
                columns=psycopg.sql.SQL(", ").join([psycopg.sql.Identifier(col) for col in chunk.columns]),
                values=psycopg.sql.SQL(", ").join(psycopg.sql.Placeholder() for _ in chunk.columns)
            )

            # Execute the insert query
            cursor.executemany(insert_query, [tuple(row) for row in chunk.itertuples(index=False)])
        # Commit the transaction
        global_connection.commit()
    except Exception as e:
        logging.error(f"Error inserting chunk into table '{table_name}': {e}")

def insertDataToPostgres(connection_params : dict, table_name : str, dataframe : pd.DataFrame, chunk_size: int = 1000) -> None:
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
        with ProcessPoolExecutor(max_workers=MAX_CORES, initializer=__connection_initializer, initargs=(connection_params,)) as executor:
            list(tqdm(executor.map(__insert_chunk_to_postgres, chunks, [table_name] * len(chunks)),
                      total=len(chunks), desc="Inserting chunks"))

        logger.info(f"Data insertion completed for table '{table_name}'. Total rows inserted: {len(dataframe)}.")
    except Exception as e:
        logger.error(f"Error during data insertion into table '{table_name}': {e}")

def updatePlayersMaxElo(connection_params : dict) -> None:
    """
    Update the max ELO of players in the PostgreSQL database.
    :param connection_params: Dictionary of database connection parameters.
    """
    try:
        with psycopg.connect(**connection_params, autocommit=True) as connection:
            connection.execute("SELECT update_players_max_elo()")

        logger.info("Players' max ELO updated successfully.")
    except Exception as e:
        logger.error(f"Error updating players' max ELO: {e}")

def addNewPGNtoDatabase(PGNFiles: list[str], db_params: dict, table_names: dict) -> None:
    """
    Add new PGN files to the PostgreSQL database.
    :param PGNFiles: List of paths to the PGN files.
    :param db_params: Dictionary of database connection parameters.
    :param table_names: Dictionary containing the table names for "players", "openings", and "games" in the database.
    """
    try:
        players_table = table_names.get("players", "players")
        openings_table = table_names.get("openings", "openings")
        games_table = table_names.get("games", "games")

        # Read PGN files and convert to DataFrame
        rawPGN = PGNtoDataFrame(PGNFiles)

        # Connect to the database
        with psycopg.connect(**db_params) as connection:
            # Get current existing players in the database
            with connection.cursor() as cursor:
                query = psycopg.sql.SQL("SELECT id, name FROM {player_table}").format(
                    player_table=psycopg.sql.Identifier(players_table)
                )
                players_data = cursor.execute(query).fetchall()
                DBplayers = pd.DataFrame(players_data, columns=["id", "name"])

            # Create DataFrame for new players and insert into PostgreSQL
            players = createPlayersDataFrame(rawPGN, DBplayers)
            insertDataToPostgres(db_params, players_table, players)

            # Get updated player and opening data from the database
            with connection.cursor() as cursor:
                query = psycopg.sql.SQL("SELECT id, name FROM {player_table}").format(
                    player_table=psycopg.sql.Identifier(players_table)
                )
                players_data = cursor.execute(query).fetchall()
                players = pd.DataFrame(players_data, columns=["id", "name"])

                query = psycopg.sql.SQL("SELECT id, name, pgn FROM {opening_table}").format(
                    opening_table=psycopg.sql.Identifier(openings_table)
                )
                openings_data = cursor.execute(query).fetchall()
                openings = pd.DataFrame(openings_data, columns=["id", "name", "pgn"])

            # Create the games DataFrame and insert into PostgreSQL
            games = createGamesDataFrame(rawPGN, players, openings)
            insertDataToPostgres(db_params, games_table, games)

            # Update players' max ELO in the database
            updatePlayersMaxElo(db_params)

        logger.info("PGN files successfully added to the database.")

    except Exception as e:
        logger.error(f"Error in addNewPGNtoDatabase: {e}")

def addOpeningsToDatabase(openingFiles: list[str], db_params: dict, table_names: dict) -> None:
    """
    Add new openings to the PostgreSQL database.
    :param openingFiles: List of paths to the TSV files containing opening information.
    :param db_params: Dictionary of database connection parameters.
    :param table_names: Dictionary containing the table names for "openings" in the database.
    """
    try:
        openings_table = table_names.get("openings", "openings")

        # Create DataFrame for openings and insert into PostgreSQL
        openings = createOpeningsDataFrame(openingFiles)
        insertDataToPostgres(db_params, openings_table, openings)

        logger.info("Openings successfully added to the database.")

    except Exception as e:
        logger.error(f"Error in addOpeningsToDatabase: {e}")