def colorize_node(node: dict) -> str:
    ntype = node.get("type")
    attrs = node.get("attrs", {})
    if ntype == "VULN":
        return "#e74c3c"  # red
    if ntype == "Template":
        ekus = attrs.get("ExtendedKeyUsage") or []
        risky = ("Any Purpose" in ekus) or ("Client Authentication" in ekus) or attrs.get("risky")
        return "#e67e22" if risky else "#3498db"
    if ntype in ("CA", "CADNS"):
        return "#8e44ad"
    if ntype in ("User", "USER"):
        return "#c0392b" if attrs.get("asrep_roastable") else "#2ecc71"
    if ntype in ("Group", "GROUP"):
        return "#2ecc71"
    if ntype in ("Host", "Computer"):
        return "#1abc9c" if attrs.get("is_dc") else "#95a5a6"
    if str(ntype).startswith("SPN"):
        return "#f1c40f"
    if str(ntype).startswith("SHARE"):
        return "#16a085"
    return "#7f8c8d"
