from __init__ import *
import networkx as nx
import matplotlib.pyplot as plt

if __name__ == "__main__":

	connection_params = {
		"dbname": "postgres",
		"user": "docker",
		"password": "docker",
		"host": "localhost",
		"port": 5432,
	}

	data = getPlayersOpenings(connection_params, "white", 100, 0.01)
	print(data)

	graph = getNetworkGraph(data)

	plotSpringLayout(graph, show_edge_labels=False)

	plt.show()