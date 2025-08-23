# Netdigger

**Netdigger** est une petite application graphique (Tkinter) pour extraire l’audio de vidéos (YouTube, etc.) en utilisant [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).  
Elle permet de télécharger directement en **WAV**, **FLAC**, ou **OGG**, avec un choix de fréquence d’échantillonnage, profondeur de bits et canaux.  
Un onglet *Settings* offre la personnalisation des arguments `yt-dlp`, et un onglet *About* affiche les infos du projet.

---

## Fonctionnalités

- Interface graphique simple avec 3 onglets : **Main**, **Settings**, **About**  
- Téléchargement audio via `yt-dlp`, avec suivi en direct du log  
- Paramètres audio personnalisables :  
  - Format : WAV, FLAC, OGG (Vorbis)  
  - Sample rate : 44.1 kHz, 48 kHz  
  - Profondeur : 16 bits, 24 bits  
  - Canaux : mono / stéréo  
- Gestion du binaire `yt-dlp` :  
  - Utilisation de la version système (PATH)  
  - Copie locale auto-téléchargeable (dans `~/.local/share/netdigger/bin`)  
  - Chemin personnalisé  
- Vérification de la version `yt-dlp` et mise à jour intégrée  
- Téléchargement automatique de la dernière release GitHub ou d’une version par *tag*  
- Affichage de l’aide `yt-dlp -h` intégrée  
- Icônes/logo (`gfx/`) inclus pour la fenêtre et l’onglet *About*  

---

## Installation

### Dépendances système
- Python 3.10+ (testé avec 3.12)  
- `ffmpeg` (obligatoire pour post-traiter en WAV/FLAC/OGG)  
- Git (si vous clonez le repo)  

Sous Ubuntu / Debian :
```bash
sudo apt install python3 python3-tk ffmpeg git python3-venv
```

### Récupération du code
```bash
git clone https://github.com/gurppt/netdigger.git
cd netdigger
```

### Environnement Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/netdigger.py
```

---

## Build (Linux)

Un script de build est fourni, il utilise un environnement virtuel `.venv-build/` pour compiler avec PyInstaller.

```bash
scripts/build-linux.sh
```

Le binaire est produit dans `dist/netdigger-<version>` et un symlink `dist/netdigger` pointe dessus.

---

## Installation utilisateur (menu XFCE / commande globale)

Pour installer Netdigger dans votre session utilisateur (accessible via `netdigger` en terminal et dans le menu XFCE/Whisker) :

```bash
scripts/install-desktop.sh
```

Cela :
- copie le binaire dans `~/.local/bin/netdigger` (assurez-vous que `~/.local/bin` est dans votre PATH)  
- installe les icônes au bon format dans `~/.local/share/icons/hicolor/...`  
- crée l’entrée de menu `~/.local/share/applications/netdigger.desktop`  

Redémarrez le panel XFCE si besoin :  
```bash
xfce4-panel -r
```

---

## Icônes et ressources

- `gfx/netdigger_icon.png` → icône source  
- `gfx/netdigger.ico` → icône Windows  
- `gfx/netdigger_logo.png` → logo affiché dans l’onglet About  

---

## Scripts utilitaires

- `scripts/build-linux.sh` → build Linux avec PyInstaller  
- `scripts/install-desktop.sh` → installe le binaire, les icônes et le .desktop utilisateur  
- `scripts/build-windows.ps1` → build Windows (PowerShell, non encore testé à fond)  

---

## Organisation du dépôt

```
netdigger/
├── src/
│   └── netdigger.py          # code source principal
├── gfx/                      # icônes / logos
├── scripts/                  # scripts build/install
│   ├── build-linux.sh
│   ├── build-windows.ps1
│   └── install-desktop.sh
├── requirements.txt
├── VERSION
└── README.md
```

---

## Utilisation

### Onglet Main
- Coller l’URL (YouTube ou autre)  
- Choisir le dossier de sortie  
- Cliquer **Download**  
- Suivre le log dans la zone Verbose  

### Onglet Settings
- Choisir la source `yt-dlp` (System / Local / Custom)  
- Gérer le téléchargement/MAJ de `yt-dlp`  
- Régler format, sample rate, bit depth, canaux  
- Ajouter des arguments personnalisés si besoin (`--cookies-from-browser firefox`, etc.)  
- Consulter l’aide intégrée (`yt-dlp -h`)  

### Onglet About
- Affiche le logo et les infos développeur  

---

## Licence

Bootleg Tool — usage libre mais sans garantie.
