import networkx as nx
from community import community_louvain

from __init__ import *
import sys
import os
import matplotlib.pyplot as plt
from json import load
import logging

from JSON_handling import validate_and_extract_params

# Initialize logging
logging.basicConfig(level=logging.INFO,
										format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":

	arg = sys.argv[1]
	if not arg:
		raise ValueError("Please provide a JSON file path as an argument.")

	if not os.path.isfile(arg):
		raise ValueError(f"File {arg} does not exist.")

	with (open(arg, 'r') as file):
		all_params = load(file)

	required_db_keys = ["dbname", "user", "host", "port"]
	optional_db_keys = ["password", "sslmode", "sslkey", "sslcert", "sslrootcert"]
	db_params = validate_and_extract_params(all_params, required_db_keys,
																					optional_db_keys)

	required_db_keys = ["layout", "color", "output_dir"]
	optional_db_keys = ["louvain", "min_games", "min_percent", "iterations"]
	plot_params = validate_and_extract_params(all_params, required_db_keys,
																						optional_db_keys)

	data = getPlayersOpenings(db_params, plot_params["color"], plot_params.get(
		"min_games", 50), plot_params.get("min_percent", 0.05))

	logger.info("Displaying fetched data: \n")
	print(data)

	graph = getNetworkGraph(data)

	if plot_params.get("layout") == "kamada":
		pos = nx.kamada_kawai_layout(graph)
	elif plot_params.get("layout") == "spring":
		pos = nx.spring_layout(graph, iterations=plot_params.get("iterations", 50))
	else:
		raise ValueError("Invalid layout type. Must be 'kamada' or 'spring'.")

	if plot_params.get("louvain") and plot_params["louvain"] == "True":
		partitions = community_louvain.best_partition(graph)
		plotLouvainPartitions(graph, pos, partitions, layout=plot_params["layout"])
		exportPlotToJSON(graph, pos, plot_params["output_dir"] + "output.json",
										 partitions)
	else:
		plotBasic(graph, pos, show_edge_labels=False)
		exportPlotToJSON(graph, pos, plot_params["output_dir"] + "output.json")

	plt.show()
