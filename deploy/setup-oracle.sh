#!/usr/bin/env bash
# Run ON the Oracle Free VM after Ubuntu is up and you have SSH access.
# Usage:
#   chmod +x deploy/setup-oracle.sh
#   ./deploy/setup-oracle.sh
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/analytics-forge}"
REPO_URL="${REPO_URL:-}"

echo "==> Updating system"
sudo apt-get update -y
sudo apt-get upgrade -y

echo "==> Installing Docker"
if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER" || true
fi

echo "==> Installing Docker Compose plugin (if missing)"
sudo apt-get install -y docker-compose-plugin || true

echo "==> Opening firewall ports (Ubuntu ufw + note Oracle Security List)"
if command -v ufw >/dev/null 2>&1; then
  sudo ufw allow OpenSSH || true
  sudo ufw allow 8501/tcp || true
  sudo ufw --force enable || true
fi

if [[ -n "$REPO_URL" && ! -d "$APP_DIR/.git" ]]; then
  echo "==> Cloning $REPO_URL -> $APP_DIR"
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

if [[ ! -f .env ]]; then
  echo "==> Creating .env from .env.example (edit secrets later)"
  cp -n .env.example .env || true
fi

mkdir -p data/uploads data/clean data/runs data/samples data/raw

echo "==> Building and starting Analytics Forge"
# If you just joined the docker group, you may need a new SSH session.
if docker info >/dev/null 2>&1; then
  docker compose up -d --build
else
  sudo docker compose up -d --build
fi

PUBLIC_IP="$(curl -s ifconfig.me || hostname -I | awk '{print $1}')"
echo ""
echo "============================================"
echo " Analytics Forge should be running."
echo " Open: http://${PUBLIC_IP}:8501"
echo ""
echo " IMPORTANT: In Oracle Cloud Console also allow"
echo " Ingress TCP 8501 (and 22) on the VCN Security List"
echo " / Network Security Group for this VM."
echo "============================================"
