import asyncio
import shlex
import re
import time
import os
from typing import Tuple

def mask_cmd(cmd: list) -> str:
    redacted = []
    for c in cmd:
        c = re.sub(r'(--password\s+\S+)', '--password ***', c)
        c = re.sub(r'(-p\s+\S+)', '-p ***', c)
        redacted.append(c)
    return ' '.join(shlex.quote(x) for x in redacted)

async def run_cmd(cmd: list, timeout: int = 120) -> Tuple[int, str, str]:
    print(f"[RUN] {mask_cmd(cmd)}")
    start = time.time()
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        so, se = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return (5, "", "timeout")
    dur = time.time() - start
    print(f"[EXIT] code={proc.returncode} dur={dur:.2f}s")
    return (proc.returncode, so.decode(errors="ignore"), se.decode(errors="ignore"))

def save_artifact(out_dir: str, name: str, content: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content or "")
    return path
