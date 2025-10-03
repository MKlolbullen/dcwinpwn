import json
import networkx as nx

def save_graph(G: nx.DiGraph, path: str):
    data = {
        "nodes": [{"id": n, "data": dict(G.nodes[n])} for n in G.nodes()],
        "edges": [{"src": u, "dst": v, "data": dict(G.edges[u, v])} for u, v in G.edges()]
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_graph(G: nx.DiGraph, path: str):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    G.clear()
    for n in data["nodes"]:
        G.add_node(n["id"], **n["data"])
    for e in data["edges"]:
        G.add_edge(e["src"], e["dst"], **e["data"])
