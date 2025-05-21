import networkx as nx
import matplotlib.pyplot as plt
import json
import logging
from Louvain.getData import getPartitionSummary

# Initialize logging
logging.basicConfig(level=logging.INFO,
										format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def plotBasic(
		graph: nx.Graph, pos: any, output:str, show_edge_labels: bool = True,
		figure_size: tuple = (60, 50), node_sizes: tuple = (500, 300)
) -> None:
	"""
	Plots the graph using the Kamada-Kawai layout.
	:param graph: The bipartite graph to be plotted.
	:param pos: The positions of the nodes in the graph.
	:param output: Path to the output image file.
	:param show_edge_labels: Whether to display edge labels (weights).
	:param figure_size: Size of the figure (width, height).
	:param node_sizes: Sizes of the nodes (opening, player).
	"""
	colors = ["lightblue" if graph.nodes[node]["type"] == "player" else "green"
						for
						node in
						graph.nodes]

	plt.figure(figsize=figure_size)
	nx.draw(
		graph, pos, with_labels=True, node_color=colors, edge_color="gray",
		node_size=[
			node_sizes[0] if graph.nodes[node]["type"] == "opening" else node_sizes[1]
			for node
			in graph.nodes],
		font_size=6, font_color="black", font_weight="bold",
		alpha=0.8
	)

	# Optionally, hide edge labels if too cluttered
	if show_edge_labels:
		edge_labels = nx.get_edge_attributes(graph, "weight")
		nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
																 font_size=5)
	plt.savefig(output)
	logger.info(f"Graph plotted and exported to {output}.")

def plotLouvainPartitions(
		graph: nx.Graph, pos: any, output: str, partition: any,
		show_edge_labels: bool = False,
		figure_size: tuple = (80, 65), node_sizes: tuple = (500, 300)
) -> None:
	"""
	Plots the graph with nodes colored based on Louvain partitions and separates
	players from openings using different shapes.
	:param graph: The graph to be plotted.
	:param pos: The positions of the nodes in the graph.
	:param output: Path to the output image file.
	:param partition: Louvain partitioning of the graph.
	:param show_edge_labels: Whether to display edge labels (weights).
	:param figure_size: Size of the figure (width, height).
	:param node_sizes: Sizes of the nodes (opening, player).
	"""
	logger.info("Plotting graph with Louvain partitions...")

	# Assign colors to nodes based on their community
	unique_communities = set(partition.values())
	community_colors = {community: plt.cm.tab20(i / len(unique_communities))
											for i, community in enumerate(unique_communities)}

	players = [node for node in graph.nodes if
						 graph.nodes[node]["type"] == "player"]
	openings = [node for node in graph.nodes if
							graph.nodes[node]["type"] == "opening"]

	player_colors = [community_colors[partition[node]] for node in players]
	opening_colors = [community_colors[partition[node]] for node in openings]

	plt.figure(figsize=figure_size)

	# Draw players (circles)
	nx.draw_networkx_nodes(
		graph, pos, nodelist=players, node_color=player_colors,
		node_shape="o", node_size=node_sizes[0], alpha=0.8
	)

	# Draw openings (squares)
	nx.draw_networkx_nodes(
		graph, pos, nodelist=openings, node_color=opening_colors,
		node_shape="s", node_size=node_sizes[1], alpha=0.8
	)

	nx.draw_networkx_edges(graph, pos, edge_color="gray", alpha=0.8)

	nx.draw_networkx_labels(graph, pos, font_size=8, font_color="black",
													font_weight="bold")

	if show_edge_labels:
		edge_labels = nx.get_edge_attributes(graph, "weight")
		nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
																 font_size=5)

	plt.axis("off")
	plt.tight_layout()
	plt.savefig(output)

	logger.info(
		f"Graph plotted with Louvain partitions and exported to {output}."
	)

def exportPlotToJSON(
		graph: nx.Graph, pos: any, output_file: str, partitions: dict = None
		) -> None:
	"""
	Exports the graph plot metadata to a JSON file.
	:param graph: The graph to be exported.
	:param pos: The positions of the nodes in the graph.
	:param partitions: Louvain partitions of the graph.
	:param output_file: Path to the output JSON file.
	"""
	logger.info("Exporting plot metadata to JSON file...")

	# Prepare metadata
	metadata = {
		"partitions":getPartitionSummary(graph, partitions) if partitions else [{}],
		"nodes": [
			{
				"id": node,
				"type": graph.nodes[node].get("type", "unknown"),
				"position": {"x": pos[node][0], "y": pos[node][1]},
				"community": partitions[node] if partitions else None,
				"elo": graph.nodes[node].get("elo", None),
				"play_count": graph.nodes[node].get("play_count", None),
			}
			for node in graph.nodes
		],
		"edges": [
			{
				"source": u,
				"target": v,
				"weight": graph[u][v].get("weight", 1.0)
			}
			for u, v in graph.edges
		]
	}

	# Write metadata to JSON
	with open(output_file, "w") as json_file:
		json.dump(metadata, json_file, indent=4)

	logger.info(f"Plot metadata exported to {output_file}")
