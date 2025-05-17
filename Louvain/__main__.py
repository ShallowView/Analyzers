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

	data = getPlayersOpenings(connection_params)
	print(data)

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

	# Visualize the graph
	pos = nx.kamada_kawai_layout(B)  # Position nodes
	colors = ["lightblue" if B.nodes[node]["type"] == "player" else "green" for node in
						B.nodes]

	plt.figure(figsize=(100, 80))  # Increase figure size
	nx.draw(
			B, pos, with_labels=True, node_color=colors, edge_color="gray",
			node_size=[500 if B.nodes[node]["type"] == "opening" else 400 for node
								 in B.nodes],
			font_size=8, font_color="black", font_weight="bold",
			alpha=0.8
	)

	# Optionally, hide edge labels if too cluttered
	# edge_labels = nx.get_edge_attributes(B, "weight")
	# nx.draw_networkx_edge_labels(B, pos, edge_labels=edge_labels, font_size=6)

	plt.title("Bipartite Graph of Players and Openings (Improved Readability)",
						fontsize=20)
	plt.show()