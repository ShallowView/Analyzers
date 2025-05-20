import sys
import argparse
import os
from json import load
import logging

import networkx as nx
from community import community_louvain

from Louvain import *

from DataCollection import validate_and_extract_params

# Initialize logging
logging.basicConfig(level=logging.INFO,
										format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":

	# Set up argument parser
	parser = argparse.ArgumentParser(description="Process input parameters for the Louvain algorithm.")
	parser.add_argument("-c", "--color", help="Color parameter (required).")
	parser.add_argument("-l", "--layout", help="Layout parameter (required).")
	parser.add_argument("json_file", help="Path to the JSON file (required).")
	parser.add_argument("--min_count", type=int, help="Minimum count (optional).")
	parser.add_argument("--min_percent", type=float, help="Minimum percentage (optional).")
	parser.add_argument("--Louvain", type=str, choices=["true", "false"], help="Disable Louvain (optional).")
	parser.add_argument("--iterations", type=int, help="Number of iterations (optional).")
	parser.add_argument("--gui", action='store_true', help="Show plot in new window (optional).")
	
	# Parse arguments
	args = parser.parse_args()
	
	# Validate JSON file path
	if not os.path.isfile(args.json_file):
			raise ValueError(f"File {args.json_file} does not exist.")
	
	# Assign parsed arguments to variables
	color = args.color
	layout = args.layout
	min_count = args.min_count
	min_percent = args.min_percent
	louvain = args.Louvain.lower() == "true" if args.Louvain else None
	iterations = args.iterations
	gui = args.gui

	with (open(args.json_file, 'r') as file):
		all_params = load(file)

	required_db_keys = ["dbname", "user", "host", "port"]
	optional_db_keys = ["password", "sslmode", "sslkey", "sslcert", "sslrootcert"]
	db_params = validate_and_extract_params(all_params, required_db_keys,
																					optional_db_keys)

	data = getPlayersOpenings(
		db_params,
		color,
		min_games=min_count if min_count is not None else 100,
		min_percent=min_percent if min_percent is not None else 0.01
	)

	logger.info("Displaying fetched data:")
	print(data)

	graph = getNetworkGraph(data)

	if layout == "kamada":
		pos = nx.kamada_kawai_layout(graph)
	elif layout == "spring":
		pos = nx.spring_layout(graph, iterations=iterations if iterations is not None else 50)
	else:
		raise ValueError("Invalid layout type. Must be 'kamada' or 'spring'.")

	partitions = None
	if louvain is None or louvain:
		logger.info("Calculating Louvain partitions...")
		partitions = community_louvain.best_partition(graph)
		if gui is not None and gui:
			plotLouvainPartitions(graph, pos, partitions)
	else:
		if gui is not None and gui:
			plotBasic(graph, pos, show_edge_labels=False)
		
		
	exportPlotToJSON(
		graph, 
		pos, 
		validate_and_extract_params(all_params, ["output"], [""]).get('output'), 
		partitions
	)