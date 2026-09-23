#!/bin/bash
# Copy this Maven web project onto the Mac so IntelliJ + SmartTomcat can open it.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${1:-$HOME/Projects/fsd2-web}"
mkdir -p "$DEST"
rsync -a --delete \
  --exclude '.git' \
  --exclude 'target' \
  --exclude '.idea/workspace.xml' \
  --exclude '.smarttomcat' \
  "$SRC/" "$DEST/"
echo "Copied to $DEST"
echo "In IntelliJ: File -> Open -> $DEST"
echo "Then install SmartTomcat (Marketplace) and run configuration FSD2 SmartTomcat"
