from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import networkx as nx

from discovery.run import run as discovery_run
from discovery.parsers import parse_nmap_xml

from api.graph import colorize_node
from api.snapshot import save_graph, load_graph

from core.types import Session, Target
from core.modules.ldap_enum import LdapEnum
from core.modules.smb_enum import SmbEnum
from core.modules.kerberos_enum import KerberosEnum
from core.modules.adcs_enum import AdcsEnum

app = FastAPI(title="linWinPwn-next API")
G = nx.DiGraph()

class DiscoveryRequest(BaseModel):
    domain: str

class ModuleRequest(BaseModel):
    session: dict
    target: str

class PathRequest(BaseModel):
    src: str
    dst: str
    allowed_edge_types: list[str] | None = None
    max_len: int = 20


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs/discovery")
async def start_discovery(req: DiscoveryRequest):
    summary = await discovery_run(req.domain)
    nodes, edges = parse_nmap_xml("out/discovery/scan.xml")
    for n in nodes:
        G.add_node(n["id"], **n)
    for e in edges:
        G.add_edge(e["src"], e["dst"], **e)
    return {"ok": True, "summary": summary, "nodes": len(nodes), "edges": len(edges)}


@app.post("/jobs/ldap")
async def run_ldap(req: ModuleRequest):
    mod = LdapEnum()
    res = await mod.run(Session(**req.session), Target(host=req.target))
    for n in res.nodes:
        G.add_node(n["id"], **n)
    for e in res.edges:
        G.add_edge(e["src"], e["dst"], **e)
    return {"status": res.status, "artifacts": res.artifacts}


@app.post("/jobs/smb")
async def run_smb(req: ModuleRequest):
    mod = SmbEnum()
    res = await mod.run(Session(**req.session), Target(host=req.target))
    for n in res.nodes:
        G.add_node(n["id"], **n)
    for e in res.edges:
        G.add_edge(e["src"], e["dst"], **e)
    return {"status": res.status, "artifacts": res.artifacts}


@app.post("/jobs/kerberos")
async def run_kerberos(req: ModuleRequest):
    mod = KerberosEnum()
    res = await mod.run(Session(**req.session), Target(host=req.target))
    for n in res.nodes:
        G.add_node(n["id"], **n)
    for e in res.edges:
        G.add_edge(e["src"], e["dst"], **e)
    return {"status": res.status, "artifacts": res.artifacts}


@app.post("/jobs/adcs")
async def run_adcs(req: ModuleRequest):
    mod = AdcsEnum()
    res = await mod.run(Session(**req.session), Target(host=req.target))
    for n in res.nodes:
        G.add_node(n["id"], **n)
    for e in res.edges:
        G.add_edge(e["src"], e["dst"], **e)
    return {"status": res.status, "artifacts": res.artifacts}


def _subgraph_by_edges(graph, allowed):
    if not allowed:
        return graph
    H = nx.DiGraph()
    for u, v, data in graph.edges(data=True):
        if data.get("type") in allowed:
            if u not in H:
                H.add_node(u, **graph.nodes[u])
            if v not in H:
                H.add_node(v, **graph.nodes[v])
            H.add_edge(u, v, **data)
    return H


@app.post("/graph/path")
def graph_path(req: PathRequest):
    H = _subgraph_by_edges(G, req.allowed_edge_types)
    try:
        path = nx.shortest_path(H, source=req.src, target=req.dst)
    except nx.NetworkXNoPath:
        return {"ok": False, "reason": "no_path"}
    if len(path) > req.max_len:
        return {"ok": False, "reason": "too_long", "len": len(path)}
    edges = [{"src": path[i], "dst": path[i + 1], "type": H.edges[path[i], path[i + 1]].get("type", "rel")}
             for i in range(len(path) - 1)]
    return {"ok": True, "nodes": path, "edges": edges}


@app.get("/graph")
def graph_export():
    nodes = []
    for n in G.nodes():
        data = dict(G.nodes[n])
        data["color"] = colorize_node(data)
        nodes.append({"id": n, "type": data.get("type", "Unknown"), "attrs": data, "color": data["color"]})
    edges = [{"src": u, "dst": v, "type": G.edges[u, v].get("type", "rel")} for u, v in G.edges()]
    return {"nodes": nodes, "edges": edges}


@app.post("/graph/save")
def graph_save(path: str = "out/graph_snapshot.json"):
    save_graph(G, path)
    return {"ok": True, "path": path}


@app.post("/graph/load")
async def graph_load(file: UploadFile = File(...)):
    tmp = f"out/{file.filename}"
    with open(tmp, "wb") as f:
        f.write(await file.read())
    load_graph(G, tmp)
    return {"ok": True, "path": tmp}
