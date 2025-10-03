import React, { useState } from "react";

export const Toolbar: React.FC<{ onFilter: (type?: string) => void; onSearch: (q: string) => void; }> = ({ onFilter, onSearch }) => {
  const [q, setQ] = useState("");
  const save = async () => { await fetch("/graph/save", { method: "POST" }); alert("Graph saved"); };
  const load = async (file: File) => {
    const fd = new FormData(); fd.append("file", file);
    await fetch("/graph/load", { method: "POST", body: fd }); alert("Graph loaded. Refresh to see changes.");
  };
  return (
    <div className="toolbar">
      <select onChange={(e) => onFilter(e.target.value || undefined)}>
        <option value="">All types</option>
        <option value="Host">Host</option>
        <option value="User">User</option>
        <option value="Group">Group</option>
        <option value="Template">Template</option>
        <option value="CA">CA</option>
        <option value="VULN">VULN</option>
      </select>
      <input placeholder="Search node id..." value={q} onChange={(e) => setQ(e.target.value)} />
      <button onClick={() => onSearch(q)}>Search</button>
      <button onClick={save}>Save snapshot</button>
      <input type="file" onChange={e => e.target.files && load(e.target.files[0])} />
    </div>
  );
};
