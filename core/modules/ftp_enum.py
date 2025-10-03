import time, os
from core.modules.base import Module, register_module
from core.proc import run_cmd, save_artifact
from core.types import ModuleResult

def parse_ftp_output(stdout: str, target: str):
    nodes, edges = [], []
    host_id = f"HOST:{target}"
    for line in stdout.splitlines():
        if "FTP" in line.upper():
            nodes.append({"id": f"SERVICE:{target}:21", "type": "Service",
                          "attrs": {"proto": "ftp", "banner": line.strip()}})
            edges.append({"src": host_id, "dst": f"SERVICE:{target}:21", "type": "ServiceRunsOn"})
    return nodes, edges

@register_module
class FtpEnum(Module):
    name = "ftp_enum"
    supported_auth = {"password","null"}

    async def run(self, session, target):
        start = time.strftime("%Y-%m-%dT%H:%M:%S")
        out_dir = f"out/{target.host}/ftp"
        os.makedirs(out_dir, exist_ok=True)

        cmd = ["nxc", "ftp", target.host]
        if session.user and session.password:
            cmd += ["-u", session.user, "-p", session.password]
        else:
            cmd += ["-u", "", "-p", ""]

        rc, so, se = await run_cmd(cmd, timeout=120)
        nodes, edges = parse_ftp_output(so, target.host)

        return ModuleResult(
            module=self.name, tool="netexec", target=target.host,
            status="ok" if rc == 0 else "tool_error",
            started_at=start, ended_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
            stdout_path=save_artifact(out_dir,"stdout.txt",so),
            stderr_path=save_artifact(out_dir,"stderr.txt",se),
            artifacts=[out_dir], nodes=nodes, edges=edges
        )
