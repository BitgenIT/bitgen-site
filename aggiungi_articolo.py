#!/usr/bin/env python3
"""
BItGen - Tool per aggiungere nuovi articoli all'enciclopedia
=============================================================

USO:
    python3 aggiungi_articolo.py

Ti farà domande e aggiungerà automaticamente l'articolo al file data.js.
Tutti i parametri opzionali vengono calcolati automaticamente.

REQUISITI:
    - Python 3.7+
    - Solo librerie standard (nessuna installazione necessaria)
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path


RUBRICHE = [
    "Ma cos'è?",
    "Sotto il Cofano", 
    "Digitale Pratico",
    "Miti Digitali",
    "Il Dietro le Quinte"
]

# Path al file data.js
SCRIPT_DIR = Path(__file__).parent
DATA_FILE = SCRIPT_DIR / "assets" / "js" / "data.js"


def colored(text, color):
    """Colorazione output terminale"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"


def print_header():
    print()
    print(colored("=" * 60, 'green'))
    print(colored("  BItGen - Aggiungi nuovo articolo", 'bold'))
    print(colored("=" * 60, 'green'))
    print()


def ask(prompt, required=True, multiline=False):
    """Chiede input all'utente con validazione"""
    if multiline:
        print(colored(prompt, 'yellow'))
        print(colored("(Scrivi il contenuto. Termina con una riga vuota contenente solo 'FINE')", 'blue'))
        lines = []
        while True:
            line = input()
            if line.strip() == 'FINE':
                break
            lines.append(line)
        return '\n'.join(lines)
    
    while True:
        value = input(colored(f"{prompt}: ", 'yellow')).strip()
        if value or not required:
            return value
        print(colored("Campo obbligatorio, riprova.", 'red'))


def scegli_rubrica():
    """Menu per la scelta della rubrica"""
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


def carica_contenuto_da_file():
    """Opzionale: carica il contenuto da un file esterno"""
    path = input(colored("Percorso file (o Invio per saltare): ", 'yellow')).strip()
    if not path:
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(colored(f"Errore apertura file: {e}", 'red'))
        return None


def aggiungi_articolo():
    """Procedura guidata di aggiunta articolo"""
    print_header()
    
    # 1. Titolo
    titolo = ask("Titolo dell'articolo")
    
    # 2. Rubrica
    rubrica = scegli_rubrica()
    
    # 3. Video URL (opzionale)
    print(colored("\nVideo YouTube URL (Invio se non ancora disponibile):", 'yellow'))
    video_url = input().strip() or "https://youtube.com/watch?v=placeholder"
    
    # 4. Contenuto
    print(colored("\nContenuto dell'articolo:", 'yellow'))
    print(colored("Opzione 1: scrivi qui direttamente (termina con 'FINE' su riga vuota)", 'blue'))
    print(colored("Opzione 2: carica da file (scrivi 'FILE')", 'blue'))
    primo_input = input().strip()
    
    if primo_input.upper() == 'FILE':
        contenuto = carica_contenuto_da_file()
        if not contenuto:
            print(colored("Contenuto mancante. Annullo.", 'red'))
            return
    elif primo_input.upper() == 'FINE':
        print(colored("Contenuto vuoto. Annullo.", 'red'))
        return
    else:
        # Continua a leggere righe fino a FINE
        lines = [primo_input]
        while True:
            line = input()
            if line.strip() == 'FINE':
                break
            lines.append(line)
        contenuto = '\n'.join(lines)
    
    # 5. Data (default: oggi)
    print()
    data_default = datetime.now().strftime('%Y-%m-%d')
    data = input(colored(f"Data pubblicazione [{data_default}]: ", 'yellow')).strip() or data_default
    
    # 6. Tag opzionali (verranno calcolati in auto se vuoto)
    print(colored("\nTag personalizzati (separati da virgola, o Invio per auto):", 'yellow'))
    tags_raw = input().strip()
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()] if tags_raw else None
    
    # Ricapitolazione
    print()
    print(colored("=" * 60, 'green'))
    print(colored("RIEPILOGO:", 'bold'))
    print(colored("=" * 60, 'green'))
    print(f"  Titolo:   {titolo}")
    print(f"  Rubrica:  {rubrica}")
    print(f"  Data:     {data}")
    print(f"  Video:    {video_url}")
    if tags:
        print(f"  Tag:      {', '.join(tags)}")
    else:
        print(f"  Tag:      (verranno estratti automaticamente)")
    print(f"  Contenuto: {len(contenuto)} caratteri")
    print()
    
    conferma = input(colored("Confermi l'aggiunta? [S/n]: ", 'yellow')).strip().lower()
    if conferma not in ('', 's', 'si', 'y', 'yes'):
        print(colored("Annullato.", 'red'))
        return
    
    # Scrivi nel file data.js
    if not DATA_FILE.exists():
        print(colored(f"✗ File non trovato: {DATA_FILE}", 'red'))
        return
    
    testo = DATA_FILE.read_text(encoding='utf-8')
    
    # Crea nuovo articolo in formato JS
    nuovo_articolo = costruisci_articolo_js(titolo, rubrica, data, video_url, contenuto, tags)
    
    # Inserisci prima della chiusura di articoliGrezzi (cerca "];" preceduto da "}")
    # Pattern: trova l'ultimo "}," nell'array e aggiungi dopo
    pattern = r'(const articoliGrezzi = \[[\s\S]*?)(\n\];)'
    match = re.search(pattern, testo)
    
    if not match:
        print(colored("✗ Non riesco a trovare l'array articoliGrezzi in data.js", 'red'))
        return
    
    # Se l'array ha già articoli, aggiungi una virgola e poi il nuovo
    # Se è vuoto, aggiungi solo il nuovo articolo
    contenuto_array = match.group(1)
    chiusura = match.group(2)
    
    # Controlla se l'ultimo carattere significativo è '},' o '['
    contenuto_trim = contenuto_array.rstrip()
    if contenuto_trim.endswith('['):
        # Array vuoto
        new_array = contenuto_array + '\n  ' + nuovo_articolo
    else:
        # Già ha articoli - aggiungi in cima per avere i più recenti per primi
        # In realtà aggiungiamo in fondo; l'ordinamento avviene lato JS
        # Assicuriamoci che l'ultimo articolo abbia la virgola
        if not contenuto_trim.endswith(','):
            # Aggiungi virgola prima del nuovo articolo
            contenuto_array_corretto = contenuto_array.rstrip()
            if contenuto_array_corretto.endswith('}'):
                contenuto_array_corretto += ','
            new_array = contenuto_array_corretto + '\n\n  ' + nuovo_articolo
        else:
            new_array = contenuto_array + '\n  ' + nuovo_articolo
    
    nuovo_testo = testo[:match.start()] + new_array + chiusura + testo[match.end():]
    
    # Backup
    backup_path = DATA_FILE.with_suffix('.js.bak')
    backup_path.write_text(testo, encoding='utf-8')
    
    # Scrivi nuovo contenuto
    DATA_FILE.write_text(nuovo_testo, encoding='utf-8')
    
    print()
    print(colored("✓ Articolo aggiunto con successo!", 'green'))
    print(colored(f"✓ Backup salvato in: {backup_path.name}", 'blue'))
    print()
    print(colored("Prossimo passo:", 'bold'))
    print("  1. Apri index.html nel browser per verificare")
    print("  2. Ricarica il sito sul tuo hosting (Netlify: trascina la cartella)")
    print()


def costruisci_articolo_js(titolo, rubrica, data, video_url, contenuto, tags):
    """Costruisce la stringa JS per il nuovo articolo"""
    # Escape del contenuto per template literal JS
    # Dobbiamo escape solo backtick e ${ 
    contenuto_escaped = contenuto.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
    titolo_escaped = titolo.replace('"', '\\"')
    
    js = '{\n'
    js += f'    titolo: "{titolo_escaped}",\n'
    js += f'    rubrica: "{rubrica}",\n'
    js += f'    data: "{data}",\n'
    js += f'    videoUrl: "{video_url}",\n'
    if tags:
        js += f'    tags: {tags},\n'
    js += f'    contenuto: `{contenuto_escaped}`\n'
    js += '  },'
    return js


if __name__ == "__main__":
    try:
        aggiungi_articolo()
    except KeyboardInterrupt:
        print(colored("\n\nInterrotto dall'utente.", 'yellow'))
        sys.exit(0)
    except Exception as e:
        print(colored(f"\n✗ Errore: {e}", 'red'))
        sys.exit(1)
