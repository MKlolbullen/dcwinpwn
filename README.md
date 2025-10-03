# dcwinpwn

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![NetExec](https://img.shields.io/badge/NetExec-latest-orange.svg)](https://github.com/Pennyw0rth/NetExec)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

**dcwinpwn** is a next‑generation Active Directory and network enumeration framework.  
It blends **offensive** and **defensive** security tooling into a modular backend with a graph‑based UI, designed for consultants and internal teams alike.

---

## ✨ Features

- **Modular backend** in Python 3.13 with async job queue, caching, and adaptive rate limits.
- **Discovery pipeline**: `subfinder` → `dnsx` → `nmap` (+ custom NSE) → JSON graph.
- **NetExec integration**: SMB, Kerberos, LDAP, ADCS, WinRM, MySQL, SSH, FTP, and more.
- **Graph model**: Users, Groups, Hosts, Services, Templates, CAs, SPNs, Shares, Vulnerabilities.
- **REST API** (FastAPI) for jobs, results, graph export, and path queries.
- **React + Sigma.js UI** for interactive graph visualization, filtering, and path finding.
- **Snapshot support**: save/load graph state for offline analysis.
- **OPSEC‑aware**: adaptive rate limiting, caching, and dry‑run planning.

---

## 📦 Installation

### Requirements
- Linux (Debian/Ubuntu/Kali recommended)
- Python 3.13
- Go (for ProjectDiscovery tools)
- Node.js (for UI)

### Quick start

```bash
# Clone repo
git clone https://github.com/MKlolbullen/dcwinpwn.git
cd dcwinpwn

# Install dependencies
sudo bash scripts/install_deps.sh

# Activate venv
source .venv/bin/activate

# Bootstrap discovery + API
bash scripts/bootstrap.sh example.com
