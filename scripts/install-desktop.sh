#!/usr/bin/env bash
set -euo pipefail

APPDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$APPDIR/dist"

# --- Trouver le binaire à installer ---
BIN="$DIST/netdigger"
if [[ ! -x "$BIN" ]]; then
  BIN_CANDIDATE="$(ls -1t "$DIST"/netdigger-* 2>/dev/null | head -n1 || true)"
  if [[ -n "${BIN_CANDIDATE:-}" && -x "$BIN_CANDIDATE" ]]; then
    BIN="$BIN_CANDIDATE"
  else
    echo "[err] Binaire introuvable dans $DIST. Lance d'abord scripts/build-linux.sh"
    exit 1
  fi
fi
install -Dm755 "$BIN" "$HOME/.local/bin/netdigger"

# --- Installer icônes hicolor (si ImageMagick dispo) ---
ICON_SRC="$APPDIR/gfx/netdigger_icon.png"
BASE="$HOME/.local/share/icons/hicolor"
if [[ -f "$ICON_SRC" ]]; then
  mkdir -p "$BASE"/{16x16,24x24,32x32,48x48,64x64,128x128,256x256}/apps
  if command -v convert >/dev/null 2>&1; then
    for sz in 16 24 32 48 64 128 256; do
      convert "$ICON_SRC" -resize "${sz}x${sz}" "$BASE/${sz}x${sz}/apps/netdigger.png"
    done
  else
    # fallback: au moins 48x48
    install -Dm644 "$ICON_SRC" "$BASE/48x48/apps/netdigger.png"
  fi
else
  echo "[warn] Icône source absente: $ICON_SRC"
fi

# --- .desktop ---
DESKTOP_FILE="$HOME/.local/share/applications/netdigger.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Netdigger
Comment=Extraire l'audio (yt-dlp) en WAV/FLAC/OGG
Exec=$HOME/.local/bin/netdigger
Icon=netdigger
Terminal=false
Categories=AudioVideo;Audio;Utility;
StartupWMClass=Netdigger
TryExec=$HOME/.local/bin/netdigger
EOF

# --- Rafraîchir caches ---
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi
# Redémarrer le panel pour que Whisker recharge
if command -v xfce4-panel >/dev/null 2>&1; then
  xfce4-panel -r
fi

echo "[ok] Install OK."
echo "- Commande : netdigger"
echo "- Menu : Netdigger (Multimédia/Utilitaires)"
