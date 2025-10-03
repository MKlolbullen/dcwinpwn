import time
import os
import json
from core.modules.base import Module
from core.proc import run_cmd, save_artifact
from core.types import ModuleResult

def parse_certipy_json(json_path: str):
    nodes, edges = [], []
    if not os.path.exists(json_path):
        return nodes, edges
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # CAs
    for ca in data.get("CertificateAuthorities", []):
        ca_name = ca.get("Name") or ca.get("CN") or "UnknownCA"
        ca_id = f"CA:{ca_name}"
        nodes.append({"id": ca_id, "type": "CA", "attrs": ca})
        dns = ca.get("DnsHostName")
        dns_list = dns if isinstance(dns, list) else [dns]
        for d in dns_list:
            if d:
                dns_id = f"CADNS:{d}"
                nodes.append({"id": dns_id, "type": "CADNS", "attrs": {"dns": d}})
                edges.append({"src": ca_id, "dst": dns_id, "type": "HasDNS"})

    # Templates
    tmpl_index = {}
    for tmpl in data.get("CertificateTemplates", []):
        tname = tmpl.get("Name") or tmpl.get("CN") or "UnknownTemplate"
        tid = f"TEMPLATE:{tname}"
        tmpl_index[tname] = tid
        nodes.append({"id": tid, "type": "Template", "attrs": tmpl})
        ca_ref = tmpl.get("CA") or tmpl.get("CAName")
        if ca_ref:
            edges.append({"src": tid, "dst": f"CA:{ca_ref}", "type": "OnCA"})
        ekus = tmpl.get("ExtendedKeyUsage") or []
        if any(e in ekus for e in ["Client Authentication", "Any Purpose"]):
            nodes.append({"id": f"FLAG:{tname}:Auth", "type": "TemplateFlag", "attrs": {"ekus": ekus}})
            edges.append({"src": tid, "dst": f"FLAG:{tname}:Auth", "type": "HasFlag"})
        perms = tmpl.get("Permissions", {})
        for grant_type, principals in perms.items():
            for p in principals or []:
                prefix = "USER" if "@" in p else "GROUP"
                pid = f"{prefix}:{p}"
                nodes.append({"id": pid, "type": prefix, "attrs": {"principal": p}})
                edges.append({"src": pid, "dst": tid, "type": f"{grant_type}"})

    # Vulnerabilities
    for vul in data.get("Vulnerabilities", []):
        esc = vul.get("Type") or "ESC?"
        target = vul.get("TargetTemplate") or vul.get("Template") or vul.get("CA") or "Unknown"
        nid = f"VULN:{esc}:{target}"
        nodes.append({"id": nid, "type": "VULN", "attrs": vul})
        if target in tmpl_index:
            edges.append({"src": tmpl_index[target], "dst": nid, "type": "HasVuln"})
        else:
            edges.append({"src": f"CA:{target}", "dst": nid, "type": "HasVuln"})

    return nodes, edges

class AdcsEnum(Module):
    name = "adcs_enum"
    supported_auth = {"password", "ntlm", "aes", "ticket", "cert"}

    async def run(self, session, target):
        start_ts = time.strftime("%Y-%m-%dT%H:%M:%S")
        out_dir = f"out/{target.host}/adcs"
        os.makedirs(out_dir, exist_ok=True)

        json_path = os.path.join(out_dir, "certipy.json")
        cmd = [
            "certipy", "find",
            "-u", f"{session.domain}\\{session.user}", "-p", session.password,
            "-dc-ip", target.host, "--json", json_path, "-vulnerable"
        ]
        rc, so, se = await run_cmd(cmd, timeout=360)
        nodes, edges = parse_certipy_json(json_path)

        return ModuleResult(
            module=self.name, tool="certipy", target=target.host,
            status="ok" if rc == 0 else "tool_error",
            started_at=start_ts,
            ended_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            stdout_path=save_artifact(out_dir, "stdout.txt", so),
            stderr_path=save_artifact(out_dir, "stderr.txt", se),
            artifacts=[out_dir, json_path], nodes=nodes, edges=edges
        )
