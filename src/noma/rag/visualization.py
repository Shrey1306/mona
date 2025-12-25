"""Neo4j graph visualization using pyvis."""

from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship, Path
import networkx as nx
from pyvis.network import Network

from noma.config import get_config

DEFAULT_QUERY = "MATCH p=()-->() RETURN p;"


def visualize_graph(query: str = DEFAULT_QUERY, output_file: str = "graph.html") -> None:
    config = get_config()
    driver = GraphDatabase.driver(
        config.neo4j.url,
        auth=(config.neo4j.user, config.neo4j.password),
    )

    with driver.session() as session:
        data = list(session.run(query))

    graph = _build_networkx_graph(data)
    _serialize_graph_data(graph)

    net = Network(height="100%", width="100%", directed=True)
    net.from_nx(graph)

    _style_nodes(net, graph)
    _style_edges(net, graph)

    net.save_graph(output_file)
    print(f"Graph visualization saved to {output_file}")
    driver.close()


def _build_networkx_graph(data) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()

    def add_node(node: Node):
        uid = node.element_id
        if not graph.has_node(uid):
            graph.add_node(uid, labels=node._labels, properties=dict(node))

    def add_edge(rel: Relationship):
        add_node(rel.start_node)
        add_node(rel.end_node)
        uid = rel.element_id
        start_id = rel.start_node.element_id
        end_id = rel.end_node.element_id
        if not graph.has_edge(start_id, end_id, key=uid):
            graph.add_edge(start_id, end_id, key=uid, type_=rel.type, properties=dict(rel))

    def handle_path(path: Path):
        for node in path.nodes:
            add_node(node)
        for rel in path.relationships:
            add_edge(rel)

    for record in data:
        for entry in record.values():
            if isinstance(entry, Node):
                add_node(entry)
            elif isinstance(entry, Relationship):
                add_edge(entry)
            elif isinstance(entry, Path):
                handle_path(entry)

    return graph


def _serialize_graph_data(graph: nx.MultiDiGraph) -> None:
    for _, data in graph.nodes(data=True):
        if isinstance(data.get("labels"), frozenset):
            data["labels"] = list(data["labels"])

    for _, _, _, data in graph.edges(data=True, keys=True):
        for key, value in data.items():
            if isinstance(value, frozenset):
                data[key] = list(value)


def _style_nodes(net: Network, graph: nx.MultiDiGraph) -> None:
    for node in net.nodes:
        node_id = node["id"]
        props = graph.nodes[node_id].get("properties", {})
        node["label"] = props.get("id", "Unknown")
        node["title"] = (
            f"Entity Type: {props.get('entity_type', 'Unknown')}\n"
            f"Description: {props.get('description', 'No description')}\n"
            f"Source ID: {props.get('source_id', 'Unknown')}"
        )
        if props.get("entity_type") == "PERSON":
            node["color"] = "lightblue"


def _style_edges(net: Network, graph: nx.MultiDiGraph) -> None:
    for edge in net.edges:
        start, end = edge["from"], edge["to"]
        for key in graph[start][end]:
            edge_data = graph.edges[start, end, key]
            props = edge_data.get("properties", {})
            edge["label"] = edge_data.get("type_", "")
            edge["title"] = (
                f"Description: {props.get('description', 'No description')}\n"
                f"Weight: {props.get('weight', 1)}\n"
                f"Order: {props.get('order', 'Unknown')}"
            )
            edge["value"] = props.get("weight", 1)

