#!/usr/bin/env bash
# Docker Engine + plugin Compose no Ubuntu 24.04 LTS (noble).
# Uso na VPS:  sudo bash deploy/install-docker-ubuntu24.sh
set -euo pipefail

if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  echo "Execute como root: sudo bash $0"
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu noble stable" \
  >/etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker
docker --version
docker compose version
echo ""
echo "Docker pronto. Na pasta do projeto: cp .env.docker.example .env, edite SECRET_KEY e ALLOWED_HOSTS,"
echo "depois: docker compose --profile full up -d --build"
