import logging

import networkx as nx
import psycopg
import pandas as pd
from psycopg.sql import SQL, Identifier
from collections import Counter, defaultdict

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
	:param min_games: Minimum number of games played by a player to be included.
	:param min_percent: Minimum percentage of games played with an opening to be included.
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
														 		p.max_elo AS player_elo,
                                o.name   AS opening_name,
                                COUNT(*) AS times_played,
                                ROUND((COUNT(*)::decimal / pg.total_games),
                                      2) AS percentage_played
                         FROM players p
                                  JOIN public.games g ON p.id = g.{color}
                    JOIN public.openings o
                         ON o.id = g.opening
                             JOIN player_games pg ON p.id = pg.player_id
                         GROUP BY p.name, p.max_elo, o.name, pg.total_games
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
	players = data[["player_name", "player_elo"]].drop_duplicates()
	play_count = data.groupby("player_name")["times_played"].sum()
	B.add_nodes_from(
			(row["player_name"], {"bipartite": 0, "type": "player", "elo": row[
				"player_elo"], "play_count": int(play_count[row["player_name"]])})
			for _, row in players.iterrows()
	)

	# Add opening nodes
	openings = data["opening_name"].unique()
	play_count = data.groupby("opening_name")["times_played"].sum()
	B.add_nodes_from(
		(opening,
		 {"bipartite": 1, "type": "opening", "play_count": int(play_count[
																														 opening])})
		for opening in openings
	)

	# Add edges between players and openings with weights (percentages)
	for _, row in data.iterrows():
		B.add_edge(row["player_name"], row["opening_name"],
							 weight=float(row["percentage_played"]))

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
			graph.add_edge(opening, prefix, weight=1.)


def getPartitionSummary(graph: nx.Graph, partition: dict) -> list[dict]:
	"""
	Create a dictionary where the key is the most prominent opening in a partition,
	and the value is the number of elements in the partition.

	:param graph: The graph containing node attributes.
	:param partition: A dictionary mapping nodes to their partition.
	:return: A dictionary with the most prominent opening as the key and the partition size as the value.
	"""
	# Group nodes by partition
	partition_groups = defaultdict(list)
	for node, community in partition.items():
		partition_groups[community].append(node)

	partition_summary = []
	for community, nodes in partition_groups.items():
		
		openings_main = [str(node).split(':')[0] for node in nodes if
										 graph.nodes[node]["type"] == "opening"]
		openings_var = [
				{"name": node, "play_count": graph.nodes[node].get("play_count", 0)}
				for node in nodes if graph.nodes[node]["type"] == "opening"
		]
		elos = [graph.nodes[node]["elo"] for node in nodes if
					 graph.nodes[node]["type"] == "player"]
		players = [node for node in nodes if graph.nodes[node]["type"] == "player"]

		most_prominent_opening = (
			Counter(openings_main).most_common(1)[0][0] if openings_main else None
		)
		partition_summary.append({
			"id": community,
			"main_opening": most_prominent_opening,
			"player_count": len(players) if players else 0,
			"players": players,
			"variation_count": len(openings_var) if openings_main else None,
			"variations": [var["name"] for var in openings_var],
			"average_max_elo": round(sum(elos) / len(players), 1) if players else None,
			"total_play_count": sum(var["play_count"] for var in openings_var)
		})
	
	return partition_summary
