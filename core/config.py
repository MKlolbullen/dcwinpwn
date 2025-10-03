import math
import yaml

def adaptive_limits(num_subdomains: int):
    qps_host = max(0.2, 2.0 * math.exp(-num_subdomains / 500.0))
    qps_ldap = max(1.0, 20.0 * math.exp(-num_subdomains / 1000.0))
    ttl = int(900 + 60 * math.log2(1 + num_subdomains))
    return {
        "per_host_qps": qps_host,
        "per_proto_qps": {"ldap": qps_ldap, "smb": qps_host * 0.8, "mssql": qps_host * 0.6},
        "cache_ttl_sec": {"discovery": ttl, "ldap": ttl, "smb": ttl // 2},
    }

def load_config(path: str = "configs/default.yaml") -> dict:
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}
