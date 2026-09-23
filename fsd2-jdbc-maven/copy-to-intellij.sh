#!/bin/bash
# Run on the Mac to replace ~/IdeaProjects/fsd2-jdbc-maven with this project.
set -e
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/IdeaProjects/fsd2-jdbc-maven"
mkdir -p "$DEST"
rsync -a --delete \
  --exclude '.git' \
  --exclude 'target' \
  --exclude '.idea/workspace.xml' \
  "$SRC/" "$DEST/"
echo "Copied to $DEST"
echo "In IntelliJ: File -> Open -> $DEST then Maven Reload"
