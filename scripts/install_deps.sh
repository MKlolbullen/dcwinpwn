#!/usr/bin/env bash
set -euo pipefail

green() { printf "\033[32m%s\033[0m\n" "$*"; }
yellow() { printf "\033[33m%s\033[0m\n" "$*"; }
red() { printf "\033[31m%s\033[0m\n" "$*"; }

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    red "Please run as root (sudo)."; exit 1
  fi
}

detect_os() {
  . /etc/os-release
  OS_ID="${ID:-debian}"
  OS_VER="${VERSION_CODENAME:-stable}"
  green "Detected OS: $OS_ID ($OS_VER)"
}

apt_update_install() {
  yellow "Updating apt and installing base packages..."
  apt-get update
  apt-get install -y \
    build-essential curl wget git unzip jq \
    python3.13 python3.13-venv python3.13-dev \
    libssl-dev libffi-dev \
    nmap \
    gcc g++ make \
    ca-certificates \
    pkg-config \
    libldap2-dev libsasl2-dev \
    krb5-user \
    neo4j \
    nodejs npm
}

install_node_latest() {
  yellow "Installing Node.js LTS via nodesource..."
  curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
  apt-get install -y nodejs
}

install_go_latest() {
  yellow "Installing latest Go..."
  GO_VER=$(curl -s https://go.dev/VERSION?m=text)
  curl -L "https://go.dev/dl/${GO_VER}.linux-amd64.tar.gz" -o /tmp/go.tgz
  rm -rf /usr/local/go && tar -C /usr/local -xzf /tmp/go.tgz
  export PATH="/usr/local/go/bin:$PATH"
  if ! grep -q "/usr/local/go/bin" /etc/profile; then
    echo 'export PATH="/usr/local/go/bin:$PATH"' >> /etc/profile
  fi
  green "Go installed: $GO_VER"
}

install_go_tools() {
  yellow "Installing subfinder and dnsx..."
  export PATH="/usr/local/go/bin:$PATH"
  go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
  go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
  install -m 0755 "$(go env GOPATH)/bin/subfinder" /usr/local/bin/subfinder
  install -m 0755 "$(go env GOPATH)/bin/dnsx" /usr/local/bin/dnsx
  green "Go tools installed: subfinder, dnsx"
}

setup_venv() {
  yellow "Creating Python 3.13 virtual environment..."
  python3.13 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip wheel setuptools
}

install_python_pkgs() {
  yellow "Installing Python packages..."
  pip install \
    fastapi uvicorn[standard] \
    pydantic \
    networkx \
    impacket \
    ldap3 \
    python-nmap \
    requests \
    typer \
    rich \
    neo4j \
    netexec \
    certipy-ad
  green "Python packages installed."
}

install_nmap_nse_extras() {
  yellow "Custom NSE scripts will be used from discovery/nse."
}

health_check() {
  yellow "Running health checks..."
  # shellcheck disable=SC1091
  source .venv/bin/activate
  command -v subfinder >/dev/null || { red "subfinder missing"; exit 1; }
  command -v dnsx >/dev/null || { red "dnsx missing"; exit 1; }
  command -v nmap >/dev/null || { red "nmap missing"; exit 1; }
  python -c "import fastapi, networkx, impacket, ldap3, neo4j" || { red "Python libs missing"; exit 1; }
  green "Health OK."
}

main() {
  require_root
  detect_os
  apt_update_install
  install_node_latest
  install_go_latest
  install_go_tools
  setup_venv
  install_python_pkgs
  install_nmap_nse_extras
  health_check
  green "All dependencies installed. Activate venv with: source .venv/bin/activate"
}

main "$@"
