#!/usr/bin/env bash
set -euo pipefail

# Install system (apt) packages listed in config/apt-requirements.txt
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APT_LIST="$ROOT_DIR/config/apt-requirements.txt"

if [ -f "$APT_LIST" ]; then
  echo "Updating apt and installing packages from $APT_LIST"
  sudo apt-get update -y
  if [ -s "$APT_LIST" ]; then
    # Install all packages listed (one per line)
    sudo xargs -a "$APT_LIST" apt-get install -y
  else
    echo "No apt packages listed in $APT_LIST"
  fi
else
  echo "No $APT_LIST file found; skipping apt installs"
fi

echo "Installing python requirements via pip3 (requirements.txt)"
if [ -f "$ROOT_DIR/requirements.txt" ]; then
  sudo pip3 install -r "$ROOT_DIR/requirements.txt"
else
  echo "No requirements.txt found at $ROOT_DIR; skipping pip install"
fi

echo "Done."
