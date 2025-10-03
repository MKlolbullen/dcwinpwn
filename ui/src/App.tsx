import React, { useEffect, useState } from "react";
import axios from "axios";
import { SigmaContainer, useLoadGraph, useRegisterEvents, useSigma } from "@react-sigma/core";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { Toolbar } from "./components/Toolbar";
import { PathFinder } from "./components/PathFinder";

const GraphView: React.FC = () => {
  const loadGraph = useLoadGraph();
  const register = useRegisterEvents();
  const sigma = useSigma();
  const [selected, setSelected] = useState<any>(null);

  useEffect(() => {
    axios.get("/graph").then(({ data }) => {
      const g = new Graph();
      data.nodes.forEach((n: any) => {
        g.addNode(n.id, { label: n.id, type: n.type, color: n.color || "#7f8c8d", size: 6, attrs: n.attrs });
      });
      data.edges.forEach((e: any) => {
        if (g.hasNode(e.src) && g.hasNode(e.dst)) g.addEdge(e.src, e.dst, { type: e.type });
      });
      forceAtlas2.assign(g, { iterations: 200, settings: { slowDown: 5 } });
      loadGraph(g);
    });
  }, [loadGraph]);

  register("clickNode", ({ node }) => {
    const attrs = sigma.getGraph().getNodeAttributes(node);
    setSelected({ id: node, type: attrs.type, attrs });
  });

  const onFilter = (type?: string) => {
    const g = sigma.getGraph();
    g.forEachNode((n, attrs) => {
      const visible = !type || attrs.type === type;
      g.setNodeAttribute(n, "hidden", !visible);
    });
  };

  const onSearch = (q: string) => {
    const g = sigma.getGraph();
    g.forEachNode((n) => g.setNodeAttribute(n, "size", 6));
    if (g.hasNode(q)) g.setNodeAttribute(q, "size", 12);
  };

  const onHighlightPath = (nodes: string[], _edges: any[]) => {
    const g = sigma.getGraph();
    nodes.forEach((n) => {
      if (g.hasNode(n)) g.setNodeAttribute(n, "color", "#27ae60");
    });
  };

  return (
    <>
      <div className="ui-bar">
        <Toolbar onFilter={onFilter} onSearch={onSearch} />
        <PathFinder onHighlight={onHighlightPath} />
        {selected && (
          <div className="panel">
            <h3>{selected.id}</h3>
            <p>Type: {selected.type}</p>
            <pre>{JSON.stringify(selected.attrs, null, 2)}</pre>
          </div>
        )}
      </div>
    </>
  );
};

export default function App() {
  return (
    <SigmaContainer style={{ height: "100vh" }}>
      <GraphView />
    </SigmaContainer>
  );
}
