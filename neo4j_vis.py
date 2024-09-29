from neo4j import GraphDatabase
from neo4j.graph import Node, Relationship, Path
import networkx as nx
from pyvis.network import Network


# Example usage
uri = "neo4j://localhost:7687"
user = "neo4j"
password = "12345678"
query = """
MATCH p=()-->() RETURN p;
"""
output_file = "test.html"


def visualize_neo4j_graph(
    uri=uri, user=user, password=password, query=query, output_file=output_file
):
    """Visualizes a graph from Neo4j query results and saves it as an HTML file using pyvis."""

    def graph_from_cypher(data):
        """Constructs a networkx graph from the results of a neo4j cypher query.
        Nodes have fields 'labels' (frozenset) and 'properties' (dicts). Node IDs correspond to the neo4j graph.
        Edges have fields 'type_' (string) denoting the type of relation, and 'properties' (dict).
        """
        G = nx.MultiDiGraph()

        def add_node(node):
            u = node.element_id
            if G.has_node(u):
                return
            G.add_node(u, labels=node._labels, properties=dict(node))

        def add_edge(relation):
            for node in (relation.start_node, relation.end_node):
                add_node(node)
            u = relation.start_node.element_id
            v = relation.end_node.element_id
            eid = relation.element_id
            if G.has_edge(u, v, key=eid):
                return
            G.add_edge(u, v, key=eid, type_=relation.type, properties=dict(relation))

        def handle_path(path):
            for node in path.nodes:
                add_node(node)
            for rel in path.relationships:
                add_edge(rel)

        for d in data:
            for entry in d.values():
                if isinstance(entry, Node):
                    add_node(entry)
                elif isinstance(entry, Relationship):
                    add_edge(entry)
                elif isinstance(entry, Path):
                    handle_path(entry)
                else:
                    raise TypeError(f"Unrecognized object: {entry}")

        return G

    def serialize_node_labels(G):
        for node, data in G.nodes(data=True):
            if "labels" in data and isinstance(data["labels"], frozenset):
                data["labels"] = list(data["labels"])  # Convert frozenset to list

    def serialize_edge_properties(G):
        for u, v, k, data in G.edges(data=True, keys=True):
            for key, value in data.items():
                if isinstance(value, frozenset):
                    data[key] = list(value)  # Convert frozenset to list

    # Connect to Neo4j
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        # First, consume the result into a list
        data = list(session.run(query))

    # Now, you can safely pass it to the function
    G = graph_from_cypher(data)

    # Convert the frozenset to a string or list in the NetworkX graph before using Pyvis
    serialize_node_labels(G)
    serialize_edge_properties(G)

    net = Network(height="100%", width="100%", directed=True)
    net.from_nx(G)

    # Customize nodes and edges for better visualization
    for node in net.nodes:
        node_id = node["id"]
        properties = G.nodes[node_id]["properties"]

        # Customize node label and tooltip
        node["label"] = properties.get("id", "Unknown")
        node["title"] = (
            f"Entity Type: {properties.get('entity_type', 'Unknown')}\n"
            f"Description: {properties.get('description', 'No description')}\n"
            f"Source ID: {properties.get('source_id', 'Unknown')}"
        )

        # Optional: Customize node color based on entity type
        if properties.get("entity_type") == "PERSON":
            node["color"] = "lightblue"

    # Customize edges for better visualization
    for edge in net.edges:
        start = edge["from"]
        end = edge["to"]

        # Since it's a MultiDiGraph, get all the edges between 'start' and 'end'
        for key in G[start][end]:
            edge_data = G.edges[start, end, key]

            # Customize edge label and tooltip
            edge["label"] = edge_data.get("type_", "")
            edge["title"] = (
                f"Description: {edge_data['properties'].get('description', 'No description')}\n"
                f"Weight: {edge_data['properties'].get('weight', 1)}\n"
                f"Order: {edge_data['properties'].get('order', 'Unknown')}"
            )

            # Customize edge thickness based on weight
            edge["value"] = edge_data["properties"].get("weight", 1)

    # Save the graph as an HTML file
    net.save_graph(output_file)
    print(f"Graph visualization saved to {output_file}")

    # Close the Neo4j driver
    driver.close()


# Call the function
# visualize_neo4j_graph(uri, user, password, query, output_file)
