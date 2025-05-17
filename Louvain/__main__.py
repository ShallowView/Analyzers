import JSON_handling
from __init__ import *
import sys
import os
import matplotlib.pyplot as plt
from json import load

from JSON_handling import validate_and_extract_params

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
	db_params = validate_and_extract_params(all_params, required_db_keys, optional_db_keys)
	
	if all_params.get("color") not in ["white", "black"]:
			raise ValueError("Please provide a valid color (white or black)")

	if all_params.get("layout") not in ["spring", "kamada"]:
		raise ValueError("Please provide a valid layout (spring or kamada)")
			
	data = getPlayersOpenings(db_params, all_params["color"], 50, 0.05)
	print(data)

	graph = getNetworkGraph(data)

	if all_params.get("layout") == "kamada":
		plotKamadaKawai(graph, show_edge_labels=False)
	if all_params.get("layout") == "spring":
		plotSpringLayout(graph, show_edge_labels=False)

	plt.show()