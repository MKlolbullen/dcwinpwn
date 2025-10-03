import time
import os
import json
from core.modules.base import Module
from core.proc import run_cmd, save_artifact
from core.types import ModuleResult

def parse_ldapdomaindump(out_dir: str):
    nodes, edges = [], []
    idx = {}

    def add_node(nid, ntype, attrs):
        nodes.append({"id": nid, "type": ntype, "attrs": attrs})
        return nid

    users_path = os.path.join(out_dir, "domain_users.json")
    groups_path = os.path.join(out_dir, "domain_groups.json")
    comps_path = os.path.join(out_dir, "domain_computers.json")

    if os.path.exists(users_path):
        users = json.load(open(users_path, "r", encoding="utf-8"))
        for u in users:
            nid = add_node(f"USER:{u.get('dn')}", "User", u)
            idx[u.get("dn")] = nid
            # DONT_REQ_PREAUTH hint
            uac = u.get("userAccountControl") or 0
            if uac & 0x00400000:
                u["asrep_roastable"] = True

    if os.path.exists(groups_path):
        groups = json.load(open(groups_path, "r", encoding="utf-8"))
        for g in groups:
            gid = add_node(f"GROUP:{g.get('dn')}", "Group", g)
            idx[g.get("dn")] = gid

    if os.path.exists(comps_path):
        comps = json.load(open(comps_path, "r", encoding="utf-8"))
        for c in comps:
            hid = add_node(f"HOST:{c.get('dn')}", "Computer", c)
            idx[c.get("dn")] = hid

    # MemberOf edges
    for path in (users_path, groups_path):
        if not os.path.exists(path):
            continue
        entries = json.load(open(path, "r", encoding="utf-8"))
        for e in entries:
            src = idx.get(e.get("dn"))
            for m in e.get("memberOf", []):
                dst = idx.get(m)
                if src and dst:
                    edges.append({"src": src, "dst": dst, "type": "MemberOf"})

    return nodes, edges

class LdapEnum(Module):
    name = "ldap_enum"
    supported_auth = {"password", "ntlm", "aes", "ticket", "cert"}

    async def run(self, session, target):
        start = time.strftime("%Y-%m-%dT%H:%M:%S")
        out_dir = f"out/{target.host}/ldap"
        os.makedirs(out_dir, exist_ok=True)

        cmd = [
            "ldapdomaindump", target.host,
            "-u", f"{session.domain}\\{session.user}",
            "-p", session.password,
            "-o", out_dir
        ]
        rc, so, se = await run_cmd(cmd, timeout=180)
        nodes, edges = parse_ldapdomaindump(out_dir)

        return ModuleResult(
            module=self.name, tool="ldapdomaindump", target=target.host,
            status="ok" if rc == 0 else "tool_error",
            started_at=start,
            ended_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            stdout_path=save_artifact(out_dir, "stdout.txt", so),
            stderr_path=save_artifact(out_dir, "stderr.txt", se),
            artifacts=[out_dir], nodes=nodes, edges=edges
        )
