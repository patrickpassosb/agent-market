#!/usr/bin/env bash
set -euo pipefail

echo ">>> Starting EC2 Setup..."

# 1. Update system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker
if ! command -v docker &> /dev/null; then
    echo ">>> Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# 3. Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo ">>> Installing Docker Compose..."
    sudo apt-get install -y docker-compose-plugin
    # Link it if necessary, though modern docker command has 'compose' subcommand
fi

# 4. Install Git
sudo apt-get install -y git

# 5. Setup swap file (Optional but recommended for t2.micro)
if [ ! -f /swapfile ]; then
    echo ">>> Creating 1GB swap file for t2.micro performance..."
    sudo fallocate -l 1G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

echo ">>> Setup Complete! Please log out and back in for group changes to take effect."
