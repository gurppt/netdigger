#!/usr/bin/env bash
set -euo pipefail

# --- Localisation du projet ---
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APPNAME="netdigger"
VERSION_FILE="$ROOT/VERSION"
VERSION="dev"
if [[ -f "$VERSION_FILE" ]]; then
  VERSION="$(tr -d ' \t\n\r' < "$VERSION_FILE")"
fi

OUTDIR="$ROOT/dist"
BUILDDIR="$ROOT/build"
SPECPATH="$ROOT/${APPNAME}.spec"
VENV="$ROOT/.venv-build"

echo "[i] Version: $VERSION"
echo "[i] Dossier projet: $ROOT"

# --- Vérifs de base ---
command -v python3 >/dev/null 2>&1 || { echo "[err] python3 introuvable"; exit 1; }

# --- Crée/valide le venv de build ---
if [[ ! -d "$VENV" ]]; then
  echo "[i] Création du venv de build: $VENV"
  python3 -m venv "$VENV"
fi

if [[ ! -f "$VENV/bin/activate" ]]; then
  echo "[err] Fichier d'activation du venv manquant: $VENV/bin/activate"
  echo "     -> Assure-toi que python3-venv est installé, puis relance."
  exit 1
fi

# shellcheck disable=SC1090
source "$VENV/bin/activate"

python -m pip install --upgrade pip
python -m pip install pyinstaller

# --- Nettoyage précédent ---
rm -rf "$BUILDDIR" "$OUTDIR" "$SPECPATH"

# --- Build ---
echo "[i] Build en cours…"
pyinstaller \
  --name "${APPNAME}-${VERSION}" \
  --onefile \
  --noconsole \
  --add-data "gfx:gfx" \
  "src/netdigger.py"

# --- Symlink pratique ---
mkdir -p "$OUTDIR"
ln -sfn "${APPNAME}-${VERSION}" "$OUTDIR/${APPNAME}"

echo "[ok] Build OK -> $OUTDIR/${APPNAME}-${VERSION}"
echo "[ok] Raccourci -> $OUTDIR/${APPNAME}"
