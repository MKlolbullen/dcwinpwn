#!/usr/bin/env bash
set -euo pipefail

# shellcheck disable=SC1091
source .venv/bin/activate

DOMAIN="${1:-example.com}"
OUTDIR="${2:-out/bootstrap}"
mkdir -p "$OUTDIR"

echo "[*] Running subfinder for $DOMAIN..."
subfinder -all -d "$DOMAIN" -o "$OUTDIR/subdomains.txt"

NUM=$(wc -l < "$OUTDIR/subdomains.txt" || echo 0)
echo "[*] Found $NUM subdomains."

NUM_SUBS="$NUM" python - <<'PY'
import math, os, json
num = int(os.environ.get("NUM_SUBS","0"))
def adaptive_limits(n):
    import math
    qps_host = max(0.2, 2.0 * math.exp(-n/500.0))
    qps_ldap = max(1.0, 20.0 * math.exp(-n/1000.0))
    ttl = int(900 + 60 * math.log2(1 + n))
    return {
        "limits": {"per_host_qps": qps_host, "per_proto_qps": {"ldap": qps_ldap, "smb": qps_host*0.8, "mssql": qps_host*0.6}},
        "cache_ttl_sec": {"discovery": ttl, "ldap": ttl, "smb": ttl//2}
    }
cfg = adaptive_limits(num)
open("configs/default.yaml","w").write(
f"""limits:
  per_host_qps: {cfg['limits']['per_host_qps']:.2f}
  per_proto_qps:
    ldap: {cfg['limits']['per_proto_qps']['ldap']:.2f}
    smb: {cfg['limits']['per_proto_qps']['smb']:.2f}
    mssql: {cfg['limits']['per_proto_qps']['mssql']:.2f}
cache_ttl_sec:
  discovery: {cfg['cache_ttl_sec']['discovery']}
  ldap: {cfg['cache_ttl_sec']['ldap']}
  smb: {cfg['cache_ttl_sec']['smb']}
"""
)
print("Adaptive config written to configs/default.yaml")
PY

echo "[*] Starting API (uvicorn)..."
uvicorn api.main:app --host 0.0.0.0 --port 8000
