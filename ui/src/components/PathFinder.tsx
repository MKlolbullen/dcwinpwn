import React, { useState } from "react";
import axios from "axios";

export const PathFinder: React.FC<{ onHighlight: (nodes: string[], edges: any[]) => void }> = ({ onHighlight }) => {
  const [src, setSrc] = useState("");
  const [dst, setDst] = useState("");
  const [edges, setEdges] = useState<string>("");

  const run = async () => {
    const allowed = edges.split(",").map(s => s.trim()).filter(Boolean);
    const { data } = await axios.post("/graph/path", { src, dst, allowed_edge_types: allowed.length ? allowed : undefined });
    if (data.ok) onHighlight(data.nodes, data.edges);
    else alert(data.reason || "No path");
  };

  return (
    <div className="pathfinder">
      <input placeholder="Source node id (e.g., USER:...)" value={src} onChange={e => setSrc(e.target.value)} />
      <input placeholder="Target node id (e.g., GROUP:Domain Admins)" value={dst} onChange={e => setDst(e.target.value)} />
      <input placeholder="Allowed edge types (comma)" value={edges} onChange={e => setEdges(e.target.value)} />
      <button onClick={run}>Find path</button>
    </div>
  );
};
