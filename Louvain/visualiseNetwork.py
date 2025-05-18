import networkx as nx
import matplotlib.pyplot as plt


def plotKamadaKawai(
		graph: nx.Graph, show_edge_labels: bool = True,
		figure_size: tuple = (60, 50), node_sizes: tuple = (500, 300)
) -> None:
	"""
	Plots the graph using the Kamada-Kawai layout.
	:param graph: The bipartite graph to be plotted.
	:param show_edge_labels: Whether to display edge labels (weights).
	:param figure_size: Size of the figure (width, height).
	:param node_sizes: Sizes of the nodes (opening, player).
	"""
	pos = nx.kamada_kawai_layout(graph)
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


def plotSpringLayout(
		graph: nx.Graph, iterations: int = 50, show_edge_labels: bool = True,
		figure_size: tuple = (60, 50), node_sizes: tuple = (500, 300)
) -> None:
	"""
	Plots the graph using the Kamada-Kawai layout.
	:param graph: The bipartite graph to be plotted.
	:param show_edge_labels: Whether to display edge labels (weights).
	:param figure_size: Size of the figure (width, height).
	:param node_sizes: Sizes of the nodes (opening, player).
	"""
	pos = nx.spring_layout(graph, iterations=iterations)
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


def plotLouvainPartitions(
		graph: nx.Graph, partition: any, show_edge_labels: bool = False,
		figure_size: tuple = (80, 65), layout: str = "spring",
		node_sizes: tuple = (500, 300)
		) -> any:
	"""
	Plots the graph with nodes colored based on Louvain partitions and separates
	players from openings using different shapes.
	:param graph: The graph to be plotted.
	:param partition: Louvain partitioning of the graph.
	:param show_edge_labels: Whether to display edge labels (weights).
	:param figure_size: Size of the figure (width, height).
	:param layout: Layout type ('kamada' or 'spring').
	:param node_sizes: Sizes of the nodes (opening, player).
	"""

	# Assign colors to nodes based on their community
	unique_communities = set(partition.values())
	community_colors = {community: plt.cm.tab20(i / len(unique_communities))
											for i, community in enumerate(unique_communities)}

	# node_colors = [community_colors[partition[node]] for node in graph.nodes]

	players = [node for node in graph.nodes if
						 graph.nodes[node]["type"] == "player"]
	openings = [node for node in graph.nodes if
							graph.nodes[node]["type"] == "opening"]

	player_colors = [community_colors[partition[node]] for node in players]
	opening_colors = [community_colors[partition[node]] for node in openings]

	if layout == "kamada":
		pos = nx.kamada_kawai_layout(graph)
	elif layout == "spring":
		pos = nx.spring_layout(graph)
	else:
		raise ValueError("Invalid layout. Choose 'kamada' or 'spring'.")
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

	return partition
