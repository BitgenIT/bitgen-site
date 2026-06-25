#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BItGen - Tool da terminale per aggiungere nuovi articoli all'enciclopedia
=========================================================================

USO:
    python3 aggiungi_articolo.py

Alternativa testuale al Gestore Articoli grafico (bitgen_manager.py).
Usa lo stesso core robusto (bitgen_data.py): scrittura JSON atomica, backup con
data/ora e validazione automatica. Niente più rischio di corrompere data.js.

REQUISITI:
    - Python 3.7+
    - Solo librerie standard (nessuna installazione necessaria)
"""

import sys
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
import bitgen_data as bd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

RUBRICHE = [
    "Ma cos'è?",
    "Sotto il Cofano",
    "Digitale Pratico",
    "Miti Digitali",
    "Il Dietro le Quinte",
]

DATA_FILE = SCRIPT_DIR / "assets" / "js" / "data.js"
IMAGES_DIR = SCRIPT_DIR / "assets" / "images"


def colored(text, color):
    colors = {
        'green': '\033[92m', 'yellow': '\033[93m', 'red': '\033[91m',
        'blue': '\033[94m', 'bold': '\033[1m', 'end': '\033[0m',
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"


def print_header():
    print()
    print(colored("=" * 60, 'green'))
    print(colored("  BItGen - Aggiungi nuovo articolo", 'bold'))
    print(colored("=" * 60, 'green'))
    print()


def ask(prompt, required=True):
    while True:
        value = input(colored(f"{prompt}: ", 'yellow')).strip()
        if value or not required:
            return value
        print(colored("Campo obbligatorio, riprova.", 'red'))


def scegli_rubrica():
    print(colored("\nScegli la rubrica:", 'yellow'))
    for i, r in enumerate(RUBRICHE, 1):
        print(f"  {i}. {r}")
    while True:
        try:
            scelta = int(input(colored("Numero rubrica: ", 'yellow')))
            if 1 <= scelta <= len(RUBRICHE):
                return RUBRICHE[scelta - 1]
        except ValueError:
            pass
        print(colored(f"Inserisci un numero da 1 a {len(RUBRICHE)}", 'red'))


def leggi_blocco_multilinea(etichetta):
    """Legge testo multilinea: termina con una riga contenente solo FINE. 'FILE' carica da file."""
    print(colored(etichetta, 'yellow'))
    print(colored("(Termina con una riga 'FINE'. Scrivi 'FILE' per caricare da un file.)", 'blue'))
    primo = input()
    if primo.strip().upper() == 'FILE':
        path = input(colored("Percorso file: ", 'yellow')).strip()
        try:
            return Path(path).read_text(encoding='utf-8')
        except Exception as e:
            print(colored(f"Errore apertura file: {e}", 'red'))
            return ''
    if primo.strip().upper() == 'FINE':
        return ''
    lines = [primo]
    while True:
        line = input()
        if line.strip() == 'FINE':
            break
        lines.append(line)
    return '\n'.join(lines)


def copia_immagine(path_str):
    """Copia un'immagine in assets/images/ con nome pulito e univoco. Ritorna il nome file o None."""
    src = Path(path_str.strip().strip('"'))
    if not src.exists():
        print(colored(f"Immagine non trovata: {src}", 'red'))
        return None
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    stem = bd.slugify(src.stem) or "immagine"
    ext = src.suffix.lower() or ".png"
    dest = IMAGES_DIR / (stem + ext)
    n = 2
    while dest.exists():
        try:
            if dest.read_bytes() == src.read_bytes():
                break
        except OSError:
            pass
        dest = IMAGES_DIR / f"{stem}-{n}{ext}"
        n += 1
    if not dest.exists():
        shutil.copy2(str(src), str(dest))
    print(colored(f"  → immagine copiata in assets/images/{dest.name}", 'blue'))
    return dest.name


def aggiungi_articolo():
    print_header()

    if not DATA_FILE.exists():
        print(colored(f"✗ File non trovato: {DATA_FILE}", 'red'))
        return

    titolo = ask("Titolo dell'articolo")
    rubrica = scegli_rubrica()

    print(colored("\nVideo YouTube URL (Invio se non ancora disponibile):", 'yellow'))
    video_url = input().strip()
    if video_url and video_url.lower().startswith(("javascript:", "data:", "vbscript:")):
        print(colored("URL non ammesso, lo ignoro.", 'red'))
        video_url = ""
    if not video_url:
        video_url = "https://youtube.com/watch?v=placeholder"

    # Copertina opzionale
    print(colored("\nImmagine di copertina (percorso file, Invio per saltare):", 'yellow'))
    cover_path = input().strip()
    thumbnail = None
    if cover_path:
        nome = copia_immagine(cover_path)
        if nome:
            thumbnail = f"assets/images/{nome}"

    # Versione breve opzionale
    breve = leggi_blocco_multilinea(
        "\nVersione BREVE (opzionale — se compilata, nel sito appare lo switch):")

    # Versione approfondita (obbligatoria)
    contenuto = leggi_blocco_multilinea("\nVersione APPROFONDITA / completa (obbligatoria):")
    if not contenuto.strip():
        print(colored("Contenuto approfondito mancante. Annullo.", 'red'))
        return

    data_default = bd.data_oggi()
    data = input(colored(f"\nData pubblicazione [{data_default}]: ", 'yellow')).strip() or data_default

    print(colored("\nTag personalizzati (separati da virgola, o Invio per auto):", 'yellow'))
    tags_raw = input().strip()
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()] if tags_raw else None

    # Riepilogo
    print()
    print(colored("=" * 60, 'green'))
    print(colored("RIEPILOGO:", 'bold'))
    print(colored("=" * 60, 'green'))
    print(f"  Titolo:    {titolo}")
    print(f"  Rubrica:   {rubrica}")
    print(f"  Data:      {data}")
    print(f"  Video:     {video_url}")
    print(f"  Copertina: {thumbnail or '(nessuna)'}")
    print(f"  Versioni:  {'Breve + Approfondita' if breve.strip() else 'Solo approfondita'}")
    print(f"  Tag:       {', '.join(tags) if tags else '(automatici)'}")
    print(f"  Slug/id:   {bd.slugify(titolo)}")
    print()

    conferma = input(colored("Confermi l'aggiunta? [S/n]: ", 'yellow')).strip().lower()
    if conferma not in ('', 's', 'si', 'y', 'yes'):
        print(colored("Annullato.", 'red'))
        return

    # Costruisci e scrivi tramite il core robusto
    nuovo = {"titolo": titolo, "rubrica": rubrica, "data": data, "videoUrl": video_url}
    if thumbnail:
        nuovo["thumbnail"] = thumbnail
    if tags:
        nuovo["tags"] = tags
    if breve.strip():
        nuovo["contenutoBreve"] = breve.strip()
    nuovo["contenuto"] = contenuto.strip()

    try:
        articoli = bd.leggi_articoli(DATA_FILE)
        # avviso collisione slug
        nuovo_slug = bd.slugify(titolo)
        if any(bd.id_articolo(a) == nuovo_slug for a in articoli):
            print(colored(f"⚠ Attenzione: esiste già un articolo con slug «{nuovo_slug}». "
                          "Cambia leggermente il titolo per evitare URL sovrapposti.", 'red'))
        articoli.insert(0, nuovo)
        backup = bd.scrivi_articoli(DATA_FILE, articoli)
    except Exception as e:
        print(colored(f"\n✗ Errore durante il salvataggio: {e}", 'red'))
        return

    print()
    print(colored("✓ Articolo aggiunto con successo!", 'green'))
    if backup:
        print(colored(f"✓ Backup salvato in: {backup.name}", 'blue'))
    print()
    print(colored("Prossimo passo:", 'bold'))
    print("  1. Apri index.html nel browser per verificare")
    print("  2. Carica data.js e le immagini nuove sul tuo hosting/GitHub")
    print()


if __name__ == "__main__":
    try:
        aggiungi_articolo()
    except KeyboardInterrupt:
        print(colored("\n\nInterrotto dall'utente.", 'yellow'))
        sys.exit(0)
    except Exception as e:
        print(colored(f"\n✗ Errore: {e}", 'red'))
        sys.exit(1)
