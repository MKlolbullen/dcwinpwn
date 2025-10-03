import asyncio
import os
import json
from core.proc import run_cmd, save_artifact

async def subfinder(domain: str, outdir: str):
    return await run_cmd(["subfinder", "-all", "-d", domain, "-o", os.path.join(outdir, "subdomains.txt")], 600)

async def dnsx_resolve(subdomains_file: str, outdir: str):
    return await run_cmd(["dnsx", "-a", "-l", subdomains_file, "-o", os.path.join(outdir, "resolved.txt")], 300)

async def nmap_scan(resolved_file: str, outdir: str):
    ports = "22,53,88,135,389,445,636,3268,3269,5985,5986,1433,3389"
    return await run_cmd([
        "nmap", "-Pn", "-n", "-iL", resolved_file,
        "-p", ports,
        "--script", "discovery/nse/ad_dc_detect.nse,smb-os-discovery,ldap-rootdse",
        "-oX", os.path.join(outdir, "scan.xml")
    ], 1800)

async def run(domain: str, outdir: str = "out/discovery"):
    os.makedirs(outdir, exist_ok=True)
    rc1, so1, se1 = await subfinder(domain, outdir)
    rc2, so2, se2 = await dnsx_resolve(os.path.join(outdir, "subdomains.txt"), outdir)
    rc3, so3, se3 = await nmap_scan(os.path.join(outdir, "resolved.txt"), outdir)
    summary = {
        "subfinder": {"rc": rc1},
        "dnsx": {"rc": rc2},
        "nmap": {"rc": rc3}
    }
    save_artifact(outdir, "summary.json", json.dumps(summary, indent=2))
    return summary

if __name__ == "__main__":
    import sys
    asyncio.run(run(sys.argv[1] if len(sys.argv) > 1 else "example.com"))
