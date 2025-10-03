import xml.etree.ElementTree as ET

def parse_nmap_xml(path: str):
    tree = ET.parse(path)
    root = tree.getroot()
    nodes, edges = [], []

    def add_node(nid, ntype, attrs=None):
        nodes.append({"id": nid, "type": ntype, "attrs": attrs or {}})

    for host in root.findall("host"):
        addr_elem = host.find("address")
        if not addr_elem:
            continue
        addr = addr_elem.attrib.get("addr")
        host_id = f"HOST:{addr}"
        host_attrs = {"ip": addr}

        # OS hints
        osmatch = host.find("os/osmatch")
        if osmatch is not None:
            host_attrs["os"] = osmatch.attrib.get("name")

        # Ports/services
        for port in host.findall("ports/port"):
            portid = port.attrib["portid"]
            proto = port.attrib["protocol"]
            service = port.find("service")
            svc_name = service.attrib.get("name") if service is not None else "unknown"
            svc_id = f"SERVICE:{addr}:{portid}"
            add_node(svc_id, "Service", {"proto": proto, "name": svc_name})
            edges.append({"src": host_id, "dst": svc_id, "type": "ServiceRunsOn"})

        # Hostscript for AD/DC detection
        for script in host.findall("hostscript/script"):
            sid = script.attrib.get("id", "")
            out = script.attrib.get("output", "")
            if sid in ("ad_dc_detect", "ldap-rootdse"):
                host_attrs["is_dc"] = True
                if "DC=" in out:
                    host_attrs["domain_hint"] = out.strip()
            if sid == "smb-os-discovery":
                if "Domain" in out:
                    host_attrs["domain_hint"] = out.strip()

        add_node(host_id, "Host", host_attrs)

        dom = host_attrs.get("domain_hint")
        if dom:
            label = dom.split("DC=")[-1] if "DC=" in dom else dom
            domain_id = f"DOMAIN:{label}"
            add_node(domain_id, "Domain", {"raw": dom})
            edges.append({"src": domain_id, "dst": host_id, "type": "HasController" if host_attrs.get("is_dc") else "MemberHost"})

    return nodes, edges
