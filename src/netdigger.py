#!/usr/bin/env python3
# netdigger.py

import os
import sys
import stat
import threading
import queue
import subprocess
import shlex
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

APP_TITLE = "Netdigger"
DEFAULT_SR = 44100
DEFAULT_BIT_DEPTH = 16
DEFAULT_CHANNELS = 2
DEFAULT_FORMAT = "wav"  # wav, flac, ogg

HELP_HINT = "Cliquez sur 'Charger l'aide yt-dlp (-h)' pour afficher l'aide ici."
GITHUB_LATEST_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp"
GITHUB_TAG_URL_TPL = "https://github.com/yt-dlp/yt-dlp/releases/download/{tag}/yt-dlp"

APP_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))  # PyInstaller-safe

# Dossier des assets (gfx) : PyInstaller -> _MEIPASS/gfx ; Source -> projet/gfx
if hasattr(sys, "_MEIPASS"):
    ASSET_GFX_DIR = Path(sys._MEIPASS) / "gfx"
else:
    ASSET_GFX_DIR = APP_ROOT.parent / "gfx"

def _user_data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "Netdigger"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Netdigger"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
        return base / "netdigger"

LOCAL_BIN_DIR = _user_data_dir() / "bin"
LOCAL_YTDLP = LOCAL_BIN_DIR / ("yt-dlp.exe" if os.name == "nt" else "yt-dlp")

class NetdiggerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("760x600")
        self.minsize(760, 520)

        # --- Icône robuste ---
        try:
            if sys.platform.startswith("win"):
                app_ico = ASSET_GFX_DIR / "netdigger.ico"
                if app_ico.exists():
                    self.iconbitmap(default=str(app_ico))
                else:
                    app_png = ASSET_GFX_DIR / "netdigger_icon.png"
                    if app_png.exists():
                        self.iconphoto(False, tk.PhotoImage(file=str(app_png)))
            else:
                app_png = ASSET_GFX_DIR / "netdigger_icon.png"
                if app_png.exists():
                    self.iconphoto(False, tk.PhotoImage(file=str(app_png)))
        except Exception as e:
            print(f"Impossible de charger l'icône: {e}")

        self.proc = None
        self.log_queue = queue.Queue()
        self.after(100, self._drain_log_queue)

        self._init_vars()
        self._build_ui()

    def _init_vars(self):
        # Main
        self.url_var = tk.StringVar()
        self.outdir_var = tk.StringVar(value=str(Path.home() / "sample/netdigger"))

        # Settings audio
        self.extra_args_var = tk.StringVar(value="")
        self.format_var = tk.StringVar(value=DEFAULT_FORMAT)
        self.sr_var = tk.IntVar(value=DEFAULT_SR)
        self.bitdepth_var = tk.IntVar(value=DEFAULT_BIT_DEPTH)
        self.channels_var = tk.IntVar(value=DEFAULT_CHANNELS)
        self.vorbis_quality_var = tk.DoubleVar(value=5.0)

        # yt-dlp source selection
        self.ytdlp_source_var = tk.StringVar(value="local")  # system | local | custom
        self.ytdlp_custom_path_var = tk.StringVar(value=self._which("yt-dlp") or "yt-dlp")
        self.ytdlp_effective_var = tk.StringVar(value=self._resolve_ytdlp_path())

        # About
        self.about_logo = None  # PhotoImage
        self.help_loaded = False

    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=8, pady=8)

        main = ttk.Frame(nb)
        settings = ttk.Frame(nb)
        about = ttk.Frame(nb)
        nb.add(main, text="Main")
        nb.add(settings, text="Settings")
        nb.add(about, text="About")

        # -------- MAIN TAB --------
        frm = ttk.Frame(main)
        frm.pack(fill="x", padx=8, pady=8)

        ttk.Label(frm, text="URL à télécharger:").grid(row=0, column=0, sticky="w")
        url_ent = ttk.Entry(frm, textvariable=self.url_var)
        url_ent.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0,8))
        frm.columnconfigure(0, weight=1)

        ttk.Label(frm, text="Dossier de sortie:").grid(row=2, column=0, sticky="w")
        out_ent = ttk.Entry(frm, textvariable=self.outdir_var)
        out_ent.grid(row=3, column=0, sticky="we", pady=(0,8))
        ttk.Button(frm, text="Parcourir...", command=self._choose_outdir).grid(row=3, column=1, sticky="e", padx=(8,0))

        btns = ttk.Frame(main)
        btns.pack(fill="x", padx=8)
        self.download_btn = ttk.Button(btns, text="Download", command=self._on_download)
        self.download_btn.pack(side="left")
        self.stop_btn = ttk.Button(btns, text="Stop", command=self._on_stop, state="disabled")
        self.stop_btn.pack(side="left", padx=(8,0))

        log_frame = ttk.LabelFrame(main, text="Sortie / Verbose")
        log_frame.pack(fill="both", expand=True, padx=8, pady=8)
        self.log_txt = tk.Text(log_frame, height=12, wrap="word")
        self.log_txt.pack(fill="both", expand=True, side="left")
        log_scroll = ttk.Scrollbar(log_frame, command=self.log_txt.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_txt.configure(yscrollcommand=log_scroll.set)
        self._log("Prêt.\n")

        # -------- SETTINGS TAB --------
        # Source yt-dlp
        ybox = ttk.LabelFrame(settings, text="Source yt-dlp")
        ybox.pack(fill="x", padx=8, pady=8)

        src_row = ttk.Frame(ybox)
        src_row.pack(fill="x", pady=(2,2))
        ttk.Radiobutton(src_row, text="System (PATH)", variable=self.ytdlp_source_var, value="system", command=self._update_ytdlp_effective).pack(side="left")
        ttk.Radiobutton(src_row, text="Local (dossier utilisateur)", variable=self.ytdlp_source_var, value="local", command=self._update_ytdlp_effective).pack(side="left", padx=(12,0))
        ttk.Radiobutton(src_row, text="Custom", variable=self.ytdlp_source_var, value="custom", command=self._update_ytdlp_effective).pack(side="left", padx=(12,0))

        custom_row = ttk.Frame(ybox)
        custom_row.pack(fill="x", pady=(2,2))
        ttk.Label(custom_row, text="Chemin custom:").pack(side="left")
        ttk.Entry(custom_row, textvariable=self.ytdlp_custom_path_var).pack(side="left", fill="x", expand=True, padx=(8,8))
        ttk.Button(custom_row, text="Parcourir…", command=self._choose_custom_ytdlp).pack(side="left")

        eff_row = ttk.Frame(ybox)
        eff_row.pack(fill="x", pady=(2,2))
        ttk.Label(eff_row, text="Utilisé:").pack(side="left")
        self.ytdlp_effective_lab = ttk.Label(eff_row, textvariable=self.ytdlp_effective_var)
        self.ytdlp_effective_lab.pack(side="left", padx=(8,0))
        ttk.Button(eff_row, text="Vérifier version", command=self._check_version).pack(side="right")

        # Gestion copie locale
        up_box = ttk.LabelFrame(settings, text="Gestion de la copie locale (dossier utilisateur)")
        up_box.pack(fill="x", padx=8, pady=8)
        ttk.Button(up_box, text="Télécharger/Mettre à jour (latest GitHub)", command=self._download_latest_local).pack(side="left")
        ttk.Button(up_box, text="Télécharger version précise (tag)", command=self._download_tagged_local).pack(side="left", padx=(8,0))
        ttk.Button(up_box, text="Ouvrir le dossier", command=lambda: self._open_dir(LOCAL_BIN_DIR)).pack(side="left", padx=(8,0))

        # Audio
        audio_box = ttk.LabelFrame(settings, text="Format / Paramètres audio")
        audio_box.pack(fill="x", padx=8, pady=8)

        ttk.Label(audio_box, text="Format:").grid(row=0, column=0, sticky="w")
        fmt_cmb = ttk.Combobox(audio_box, textvariable=self.format_var, values=["wav", "flac", "ogg"], state="readonly", width=8)
        fmt_cmb.grid(row=0, column=1, sticky="w", padx=(8,16))
        fmt_cmb.bind("<<ComboboxSelected>>", lambda e: self._update_controls_state())

        ttk.Label(audio_box, text="Sample rate:").grid(row=0, column=2, sticky="w")
        sr_frame = ttk.Frame(audio_box)
        sr_frame.grid(row=0, column=3, sticky="w", padx=(8,16))
        ttk.Radiobutton(sr_frame, text="44.1 kHz", variable=self.sr_var, value=44100, command=self._update_controls_state).pack(side="left")
        ttk.Radiobutton(sr_frame, text="48 kHz", variable=self.sr_var, value=48000, command=self._update_controls_state).pack(side="left")

        ttk.Label(audio_box, text="Bit depth:").grid(row=1, column=0, sticky="w", pady=(8,0))
        bd_frame = ttk.Frame(audio_box)
        bd_frame.grid(row=1, column=1, sticky="w", padx=(8,16), pady=(8,0))
        ttk.Radiobutton(bd_frame, text="16", variable=self.bitdepth_var, value=16, command=self._update_controls_state).pack(side="left")
        ttk.Radiobutton(bd_frame, text="24", variable=self.bitdepth_var, value=24, command=self._update_controls_state).pack(side="left")

        ttk.Label(audio_box, text="Canaux:").grid(row=1, column=2, sticky="w", pady=(8,0))
        ch_frame = ttk.Frame(audio_box)
        ch_frame.grid(row=1, column=3, sticky="w", padx=(8,16), pady=(8,0))
        ttk.Radiobutton(ch_frame, text="Mono", variable=self.channels_var, value=1).pack(side="left")
        ttk.Radiobutton(ch_frame, text="Stéréo", variable=self.channels_var, value=2).pack(side="left")

        self.vorbis_frame = ttk.Frame(audio_box)
        self.vorbis_label = ttk.Label(self.vorbis_frame, text="Qualité Vorbis (q):")
        self.vorbis_scale = ttk.Scale(self.vorbis_frame, from_=0.0, to=10.0, orient="horizontal", variable=self.vorbis_quality_var)
        self.vorbis_value = ttk.Label(self.vorbis_frame, textvariable=tk.StringVar(value=str(self.vorbis_quality_var.get())))
        self.vorbis_quality_var.trace_add("write", lambda *args: self.vorbis_value.config(text=f"{self.vorbis_quality_var.get():.1f}"))
        self.vorbis_label.pack(side="left")
        self.vorbis_scale.pack(side="left", fill="x", expand=True, padx=8)
        self.vorbis_value.pack(side="left")

        # Arguments additionnels + tip
        extra_box = ttk.LabelFrame(settings, text="Arguments additionnels (passés à yt-dlp tels quels)")
        extra_box.pack(fill="x", padx=8, pady=8)
        ttk.Entry(extra_box, textvariable=self.extra_args_var).pack(fill="x", padx=8, pady=(8,4))
        ttk.Label(
            extra_box,
            text='Astuce : ajoutez "--cookies-from-browser firefox" en cas de problème de login.',
            foreground="#555"
        ).pack(fill="x", padx=8, pady=(0,8))

        # Aide yt-dlp (-h)
        help_box = ttk.LabelFrame(settings, text="Aide yt-dlp (-h)")
        help_box.pack(fill="both", expand=True, padx=8, pady=8)
        help_btns = ttk.Frame(help_box)
        help_btns.pack(fill="x")
        ttk.Button(help_btns, text="Charger l'aide yt-dlp (-h)", command=self._load_ytdlp_help).pack(side="left")
        ttk.Button(help_btns, text="Effacer", command=self._clear_help).pack(side="left", padx=(8,0))
        self.help_txt = tk.Text(help_box, wrap="word")
        self.help_txt.pack(fill="both", expand=True)
        self.help_txt.insert("1.0", HELP_HINT)

        self._update_controls_state()
        self._update_ytdlp_effective()

        # -------- ABOUT TAB --------
        about_inner = ttk.Frame(about)
        about_inner.pack(fill="both", expand=True)

        center = ttk.Frame(about_inner)
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = ASSET_GFX_DIR / "netdigger_logo.png"
        if logo_path.exists():
            try:
                self.about_logo = tk.PhotoImage(file=str(logo_path))
                ttk.Label(center, image=self.about_logo).pack(pady=(0,12))
            except Exception as e:
                ttk.Label(center, text=f"(Logo introuvable ou invalide: {e})").pack(pady=(0,12))
        else:
            ttk.Label(center, text="(gfx/netdigger_logo.png manquant)").pack(pady=(0,12))

        info_text = (
            "Netdigger\n"
            "Version : 0.1.0\n"
            "Auteur : Captain Cool\n"
            "Site / Repo : Suspicious Sausage Records\n"
            "Licence : bootleg tool\n"
        )
        ttk.Label(center, text=info_text, justify="center").pack()

    # ---------- Helpers UI ----------
    def _choose_outdir(self):
        d = filedialog.askdirectory(initialdir=self.outdir_var.get() or str(Path.home()))
        if d:
            self.outdir_var.set(d)

    def _choose_custom_ytdlp(self):
        path = filedialog.askopenfilename(
            title="Choisir binaire yt-dlp",
            filetypes=[("yt-dlp", "yt-dlp*"), ("Tous", "*.*")]
        )
        if path:
            self.ytdlp_custom_path_var.set(path)
            self._update_ytdlp_effective()

    def _update_ytdlp_effective(self):
        self.ytdlp_effective_var.set(self._resolve_ytdlp_path())

    def _resolve_ytdlp_path(self):
        src = self.ytdlp_source_var.get()
        if src == "local":
            return str(LOCAL_YTDLP)
        elif src == "custom":
            return self.ytdlp_custom_path_var.get().strip() or "yt-dlp"
        else:
            return self._which("yt-dlp") or "yt-dlp"

    def _update_controls_state(self):
        fmt = self.format_var.get()
        show_vorbis = (fmt == "ogg")
        if show_vorbis:
            self.vorbis_frame.grid(row=2, column=0, columnspan=4, sticky="we", pady=(8,0))
        else:
            self.vorbis_frame.grid_forget()

    # ---------- Download workflow ----------
    def _on_download(self):
        url = self.url_var.get().strip()
        outdir = self.outdir_var.get().strip()
        if not url:
            messagebox.showwarning(APP_TITLE, "Veuillez renseigner une URL.")
            return
        if not outdir:
            messagebox.showwarning(APP_TITLE, "Veuillez choisir un dossier de sortie.")
            return
        Path(outdir).mkdir(parents=True, exist_ok=True)

        cmd = self._build_command(url, outdir)
        self._log(f"\n$ {' '.join(shlex.quote(x) for x in cmd)}\n")

        self.download_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.proc = None

        t = threading.Thread(target=self._run_subprocess, args=(cmd,))
        t.daemon = True
        t.start()

    def _on_stop(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
            except Exception:
                pass

    def _build_command(self, url, outdir):
        ytdlp = self.ytdlp_effective_var.get() or "yt-dlp"
        fmt = self.format_var.get()
        sr = int(self.sr_var.get())
        bd = int(self.bitdepth_var.get())
        ch = int(self.channels_var.get())
        extra = self.extra_args_var.get().strip()

        if bd == 16:
            sample_fmt = "s16"
        elif bd == 24:
            sample_fmt = "s24le"
        else:
            sample_fmt = "s16"

        ffargs = ["-ar", str(sr), "-ac", str(ch)]
        if fmt in ("wav", "flac"):
            ffargs.extend(["-sample_fmt", sample_fmt])
        if fmt == "ogg":
            q = max(0.0, min(10.0, float(self.vorbis_quality_var.get())))
            ffargs.extend(["-q:a", f"{q:.1f}"])

        out_tpl = str(Path(outdir) / "%(title).200B [%(id)s].%(ext)s")
        cmd = [ytdlp, "-x", "--audio-format", fmt, "--audio-quality", "0",
               "--postprocessor-args", f"ffmpeg:{' '.join(shlex.quote(a) for a in ffargs)}",
               "-o", out_tpl, url]
        if extra:
            cmd.extend(shlex.split(extra))
        return cmd

    def _run_subprocess(self, cmd):
        try:
            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            assert self.proc.stdout is not None
            for line in self.proc.stdout:
                self.log_queue.put(line.rstrip("\n"))
            rc = self.proc.wait()
            self.log_queue.put(f"\nTerminé. Code de sortie: {rc}\n")
        except FileNotFoundError:
            self.log_queue.put("Erreur: yt-dlp introuvable. Vérifiez la source dans Settings.")
        except Exception as e:
            self.log_queue.put(f"Erreur: {e}")
        finally:
            self.after(0, self._reset_buttons)

    def _reset_buttons(self):
        self.download_btn.config(state="normal")
        self.stop_btn.config(state="disabled")

    def _drain_log_queue(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                self._log(line + "\n")
        except queue.Empty:
            pass
        self.after(100, self._drain_log_queue)

    def _log(self, text):
        self.log_txt.insert("end", text)
        self.log_txt.see("end")

    # ---------- yt-dlp: help / version ----------
    def _load_ytdlp_help(self):
        self.help_txt.delete("1.0", "end")
        self.help_txt.insert("1.0", "Chargement de l'aide...\n")
        ytdlp = self.ytdlp_effective_var.get() or "yt-dlp"
        def worker():
            try:
                out = subprocess.check_output([ytdlp, "-h"], stderr=subprocess.STDOUT, text=True)
            except FileNotFoundError:
                out = "Erreur: yt-dlp introuvable. Choisissez la source ou téléchargez une copie locale."
            except subprocess.CalledProcessError as e:
                out = e.output or str(e)
            self.help_txt.after(0, lambda: self._set_help(out))
        threading.Thread(target=worker, daemon=True).start()

    def _set_help(self, text):
        self.help_txt.delete("1.0", "end")
        self.help_txt.insert("1.0", text)

    def _clear_help(self):
        self.help_txt.delete("1.0", "end")
        self.help_txt.insert("1.0", HELP_HINT)

    def _check_version(self):
        ytdlp = self.ytdlp_effective_var.get() or "yt-dlp"
        try:
            out = subprocess.check_output([ytdlp, "--version"], stderr=subprocess.STDOUT, text=True).strip()
            messagebox.showinfo(APP_TITLE, f"yt-dlp version: {out}\n\nChemin: {ytdlp}")
        except FileNotFoundError:
            messagebox.showerror(APP_TITLE, "yt-dlp introuvable. Choisissez la source ou téléchargez une copie locale.")
        except subprocess.CalledProcessError as e:
            messagebox.showerror(APP_TITLE, f"Erreur: {e.output or e}")

    # ---------- Local downloader ----------
    def _download_latest_local(self):
        self._download_local_from_url(GITHUB_LATEST_URL, label="latest")

    def _download_tagged_local(self):
        d = tk.Toplevel(self)
        d.title("Télécharger version par tag")
        d.grab_set()
        ttk.Label(d, text="Tag GitHub (ex: 2025.07.01):").pack(padx=12, pady=(12,4))
        v = tk.StringVar()
        ent = ttk.Entry(d, textvariable=v, width=28)
        ent.pack(padx=12, pady=(0,12))
        status = ttk.Label(d, text="")
        status.pack(padx=12, pady=(0,8))

        def run():
            tag = v.get().strip()
            if not tag:
                status.config(text="Veuillez saisir un tag.")
                return
            url = GITHUB_TAG_URL_TPL.format(tag=tag)
            status.config(text="Téléchargement…")
            threading.Thread(target=lambda: self._download_local_from_url(url, label=tag, status_label=status), daemon=True).start()

        ttk.Button(d, text="Télécharger", command=run).pack(pady=(0,12))
        ttk.Button(d, text="Fermer", command=d.destroy).pack(pady=(0,12))

    def _download_local_from_url(self, url, label="latest", status_label=None):
        try:
            LOCAL_BIN_DIR.mkdir(parents=True, exist_ok=True)
            tmp_path = LOCAL_BIN_DIR / ("yt-dlp.tmp")
            final_path = LOCAL_YTDLP

            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(req) as r, open(tmp_path, "wb") as f:
                chunk = r.read(8192)
                while chunk:
                    f.write(chunk)
                    chunk = r.read(8192)

            mode = os.stat(tmp_path).st_mode
            os.chmod(tmp_path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            tmp_path.replace(final_path)

            msg = f"Copie locale mise à jour ({label}).\n{final_path}"
            self._toast(msg)
            if status_label:
                status_label.after(0, lambda: status_label.config(text=msg))

            if self.ytdlp_source_var.get() == "local":
                self._update_ytdlp_effective()

        except (URLError, HTTPError) as e:
            msg = f"Erreur réseau: {e}"
            self._toast(msg)
            if status_label:
                status_label.after(0, lambda: status_label.config(text=msg))
        except Exception as e:
            msg = f"Erreur: {e}"
            self._toast(msg)
            if status_label:
                status_label.after(0, lambda: status_label.config(text=msg))

    def _toast(self, text):
        self._log(text + "\n")

    # ---------- utils ----------
    @staticmethod
    def _which(cmd):
        from shutil import which
        return which(cmd)

    @staticmethod
    def _open_dir(path: Path):
        path.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("linux"):
            subprocess.Popen(["xdg-open", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        elif os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]

def main():
    app = NetdiggerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
