import time, os
from core.modules.base import Module, register_module
from core.proc import run_cmd, save_artifact
from core.types import ModuleResult

def parse_ssh_output(stdout: str, target: str):
    nodes, edges = [], []
    host_id = f"HOST:{target}"
    for line in stdout.splitlines():
        if "SSH" in line:
            nodes.append({"id": f"SERVICE:{target}:22", "type": "Service",
                          "attrs": {"proto": "ssh", "banner": line.strip()}})
            edges.append({"src": host_id, "dst": f"SERVICE:{target}:22", "type": "ServiceRunsOn"})
    return nodes, edges

@register_module
class SshEnum(Module):
    name = "ssh_enum"
    supported_auth = {"password","key","null"}

    async def run(self, session, target):
        start = time.strftime("%Y-%m-%dT%H:%M:%S")
        out_dir = f"out/{target.host}/ssh"
        os.makedirs(out_dir, exist_ok=True)

        cmd = ["nxc", "ssh", target.host]
        if session.user and session.password:
            cmd += ["-u", session.user, "-p", session.password]
        elif session.cert_path:
            cmd += ["-u", session.user or "", "--key", session.cert_path]
        else:
            cmd += ["-u", "", "-p", ""]

        rc, so, se = await run_cmd(cmd, timeout=120)
        nodes, edges = parse_ssh_output(so, target.host)

        return ModuleResult(
            module=self.name, tool="netexec", target=target.host,
            status="ok" if rc == 0 else "tool_error",
            started_at=start, ended_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            stdout_path=save_artifact(out_dir,"stdout.txt",so),
            stderr_path=save_artifact(out_dir,"stderr.txt",se),
            artifacts=[out_dir], nodes=nodes, edges=edges
        )
