import time
import os
from core.modules.base import Module
from core.proc import run_cmd, save_artifact
from core.types import ModuleResult

def parse_netexec_output(stdout: str, target: str):
    nodes, edges = [], []
    host_id = f"HOST:{target}"
    host_attrs = {}

    for line in stdout.splitlines():
        ls = line.strip()
        if "Windows" in ls and "Build" in ls:
            host_attrs["os"] = ls
        if "Share" in ls and ":" in ls:
            parts = ls.split()
            share = parts[-2] if len(parts) >= 2 else "unknown"
            share_id = f"SHARE:{target}:{share}"
            nodes.append({"id": share_id, "type": "Share", "attrs": {}})
            edges.append({"src": host_id, "dst": share_id, "type": "HasShare"})
        if "Pwn3d!" in ls:
            host_attrs["admin_access"] = True

    nodes.append({"id": host_id, "type": "Host", "attrs": host_attrs})
    return nodes, edges

class SmbEnum(Module):
    name = "smb_enum"
    supported_auth = {"password", "ntlm", "aes", "ticket", "cert", "null"}

    async def run(self, session, target):
        start = time.strftime("%Y-%m-%dT%H:%M:%S")
        out_dir = f"out/{target.host}/smb"
        os.makedirs(out_dir, exist_ok=True)

        cmd = ["nxc", "smb", target.host]
        if session.user and session.password:
            cmd += ["-u", session.user, "-p", session.password]
        elif session.ntlm_hash:
            cmd += ["-u", session.user or "", "-H", session.ntlm_hash]
        elif session.aes_key:
            cmd += ["-u", session.user or "", "--aesKey", session.aes_key]
        elif session.ticket_path:
            cmd += ["-k"]
        else:
            cmd += ["-u", "", "-p", ""]

        rc, so, se = await run_cmd(cmd, timeout=180)
        nodes, edges = parse_netexec_output(so, target.host)

        return ModuleResult(
            module=self.name, tool="netexec", target=target.host,
            status="ok" if rc == 0 else "tool_error",
            started_at=start,
            ended_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            stdout_path=save_artifact(out_dir, "stdout.txt", so),
            stderr_path=save_artifact(out_dir, "stderr.txt", se),
            artifacts=[out_dir], nodes=nodes, edges=edges
        )
