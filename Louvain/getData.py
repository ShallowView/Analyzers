import logging

import networkx as nx
import psycopg
import pandas as pd
from psycopg.sql import SQL, Identifier

# Initialize logging
logging.basicConfig(level=logging.INFO,
										format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def getPlayersOpenings(
		connection_params: dict, color: str, min_games: int = 100, 
		min_percent: float = 0.01
) -> pd.DataFrame:
	"""
	Fetches player-opening data based on the specified color (white or black).

	:param connection_params: Dictionary containing database connection parameters.
	:param color: The color to filter by ('white' or 'black').
	:return: DataFrame containing player-opening data.
	"""
	
	logger.info("Fetching player-opening data...")
	
	if color not in ["white", "black"]:
		raise ValueError("Invalid color. Must be 'white' or 'black'.")

	try:
		with psycopg.connect(**connection_params) as conn:
			with conn.cursor() as cursor:
				from_query = SQL("""
                         WITH player_games AS (SELECT p.id     AS player_id,
                                                      COUNT(*) AS total_games
                                               FROM players p
                                                        JOIN public.games g ON p.id = g.{color}
                                               GROUP BY p.id)
                         SELECT p.name   AS player_name,
                                o.name   AS opening_name,
                                COUNT(*) AS times_played,
                                ROUND((COUNT(*)::decimal / pg.total_games),
                                      2) AS percentage_played
                         FROM players p
                                  JOIN public.games g ON p.id = g.{color}
                    JOIN public.openings o
                         ON o.id = g.opening
                             JOIN player_games pg ON p.id = pg.player_id
                         GROUP BY p.name, o.name, pg.total_games
                         HAVING COUNT(*) >= {min_count}
                            AND (COUNT(*)::decimal / pg.total_games) >= {min_percent}
												 """).format(color=Identifier(color),
																		 min_count=min_games,
																		 min_percent=min_percent)

				cursor.execute(from_query)
				result = cursor.fetchall()
				
				logger.info("Finished fetching player-opening data.")
				
				return pd.DataFrame(result,
														columns=[desc[0] for desc in cursor.description])
	except Exception as e:
		logger.error(f"Error fetching data: {e}")
		return pd.DataFrame()


def getNetworkGraph(data: pd.DataFrame) -> nx.Graph:
	"""
	Generates a bipartite graph from the given data.
	:param data: DataFrame containing opening percentage per player data.
	:return: Bipartite graph with players and openings as nodes.
	"""

	B = nx.Graph()

	# Add player nodes
	players = data["player_name"].unique()
	B.add_nodes_from(players, bipartite=0, type="player")

	# Add opening nodes
	openings = data["opening_name"].unique()
	B.add_nodes_from(openings, bipartite=1, type="opening")

	# Add edges between players and openings with weights (percentages)
	for _, row in data.iterrows():
		B.add_edge(row["player_name"], row["opening_name"],
							 weight=row["percentage_played"])

	__add_opening_edges(B, data)

	return B


def __add_opening_edges(graph: nx.Graph, data: pd.DataFrame) -> None:
	"""
	Adds edges between openings whose name before the ':' character matches
	the full name of another opening node, using the provided DataFrame.

	:param graph: The bipartite graph containing player and opening nodes.
	:param data: DataFrame containing opening names.
	"""
	# Extract unique opening names from the DataFrame
	openings = data["opening_name"].unique()

	# Create a set of opening names for quick lookup
	opening_set = set(openings)

	# Iterate through openings and add edges based on the condition
	for opening in openings:
		if ':' in opening:
			prefix = opening.split(':', 1)[0]  # Extract the part before ':'
			if prefix not in opening_set:
				# Add the prefix as a new node
				graph.add_node(prefix, bipartite=1, type="opening")
				opening_set.add(prefix)  # Update the set
			# Add the edge between the opening and the prefix
			graph.add_edge(opening, prefix, weight=1)
