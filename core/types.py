from dataclasses import dataclass
from typing import List, Dict, Optional, Literal

Status = Literal["ok", "partial", "auth_error", "net_error", "tool_error"]

@dataclass
class Session:
    domain: Optional[str] = None
    dc_ip: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    ntlm_hash: Optional[str] = None
    aes_key: Optional[str] = None
    ticket_path: Optional[str] = None
    cert_path: Optional[str] = None

@dataclass
class Target:
    host: str
    proto: Optional[str] = None
    tags: Dict[str, str] = None

@dataclass
class ModuleResult:
    module: str
    tool: str
    target: str
    status: Status
    started_at: str
    ended_at: str
    stdout_path: str
    stderr_path: str
    artifacts: List[str]
    nodes: List[Dict]
    edges: List[Dict]
