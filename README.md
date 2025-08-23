# Netdigger

**Netdigger** est une petite application graphique (Tkinter) pour extraire l’audio de vidéos (YouTube, etc.) en utilisant [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).  
Elle permet de télécharger directement en **WAV**, **FLAC**, ou **OGG**, avec un choix de fréquence d’échantillonnage, profondeur de bits et canaux.  
Un onglet *Settings* offre la personnalisation des arguments `yt-dlp`, et un onglet *About* affiche les infos du projet.

---

## Fonctionnalités

- GUI minimaliste (Tkinter) avec 3 onglets : **Main**, **Settings**, **About**.
- Téléchargement audio via `yt-dlp`, avec suivi en direct du log.
- Paramètres audio personnalisables :
  - Format : WAV, FLAC, OGG (Vorbis).
  - Sample rate : 44.1 kHz, 48 kHz.
  - Profondeur : 16 bits, 24 bits.
  - Canaux : mono / stéréo.
- Gestion du binaire `yt-dlp` :
  - Utilisation de la version système (PATH).
  - Ou d’une **copie locale auto-téléchargeable** (dans `~/.local/share/netdigger/bin`).
  - Ou d’un chemin personnalisé.
- Vérification de la version `yt-dlp`.
- Téléchargement automatique de la dernière release GitHub ou d’une version par *tag*.
- Affichage de l’aide `yt-dlp -h` intégrée dans l’onglet *Settings*.
- Icônes/logo (`gfx/`) inclus pour la fenêtre et l’onglet *About*.

---

## Installation

### Dépendances système

- **Python 3.10+** (testé avec 3.12).
- `ffmpeg` (obligatoire pour post-traiter en WAV/FLAC/OGG).
- Git (si vous clonez le repo).

Sous Ubuntu / Debian :
```bash
sudo apt install python3 python3-tk ffmpeg git

---

### Récupération du code
git clone https://github.com/<ton-user>/netdigger.git
cd netdigger


---

### Environnement Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/netdigger.py

---

### Icônes et ressources
Icônes et ressources

gfx/netdigger_icon.png → icône fenêtre (Linux/macOS).
gfx/netdigger.ico → icône (Windows).
gfx/netdigger_logo.png → logo affiché dans l’onglet About.

---

### Scripts Utilitaires

Build Linux (binaire standalone)

scripts/build-linux.sh

Produit dist/netdigger-<version> et un symlink dist/netdigger.



Installation utilisateur (menu XFCE + commande netdigger)

scripts/install-desktop.sh

Copie dans ~/.local/bin/netdigger.
Crée ~/.local/share/applications/netdigger.desktop.


Build Windows (PowerShell)

scripts/build-windows.ps1

Produit dist/netdigger-<version>.exe.

---

### Organisation du dépot

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

---


### Utilisation :


Onglet Main :
Coller l’URL (YouTube ou autre).
Choisir le dossier de sortie.
Cliquer Download.
Suivre le log dans la zone Verbose.

Onglet Settings :
Choisir source yt-dlp (System / Local / Custom).
Gérer le téléchargement/MAJ de yt-dlp.
Régler format, sample rate, bit depth, canaux.
Ajouter des arguments personnalisés si besoin (--cookies-from-browser firefox, etc.).
Consulter l’aide intégrée (yt-dlp -h).

Onglet About :
Affiche le logo + infos développeur.
