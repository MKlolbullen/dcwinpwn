from core.proc import run_cmd

async def run_linwinpwn(module_name: str, args: list, timeout: int = 180):
    cmd = ["bash", "linWinPwn.sh", module_name] + args
    return await run_cmd(cmd, timeout=timeout)
