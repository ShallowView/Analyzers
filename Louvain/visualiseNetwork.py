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
