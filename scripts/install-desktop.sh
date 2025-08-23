#!/usr/bin/env bash
set -euo pipefail

APPDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$APPDIR/dist"
BIN="$DIST/netdigger"  # symlink créé au build
ICON="$APPDIR/gfx/netdigger_icon.png"

install -Dm755 "$BIN" "$HOME/.local/bin/netdigger"

mkdir -p "$HOME/.local/share/applications"
cat > "$HOME/.local/share/applications/netdigger.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Netdigger
Comment=Extraire l'audio (yt-dlp) en WAV/FLAC/OGG
Exec=$HOME/.local/bin/netdigger
Icon=$ICON
Terminal=false
Categories=AudioVideo;Audio;Utility;
StartupWMClass=Netdigger
EOF

update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true

echo "Install OK."
echo "- Commande : netdigger"
echo "- Menu : Netdigger (Multimédia/Utilitaires)"
