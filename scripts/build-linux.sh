#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERSION="$(cat VERSION)"
OUTDIR="$ROOT/dist"
APPNAME="netdigger"
BINNAME="$APPNAME-$VERSION"

# Dépendances build (une fois pour toutes)
python3 -m pip install --user --upgrade pip pyinstaller

# Nettoyage
rm -rf build dist "$APPNAME.spec"

# Build one-file, on embarque juste les assets gfx
pyinstaller \
  --name "$BINNAME" \
  --onefile \
  --noconsole \
  --add-data "gfx:gfx" \
  "src/netdigger.py"

# Raccourci "netdigger" => version courante
mkdir -p "$OUTDIR"
ln -sf "$BINNAME" "$OUTDIR/$APPNAME"

echo "Build OK -> $OUTDIR/$BINNAME"
