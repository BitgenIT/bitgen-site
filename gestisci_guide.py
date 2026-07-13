#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BItGen - Gestore delle GUIDE (percorsi di lettura)
==================================================

Crea e modifica le "guide": percorsi ordinati di articoli GIÀ presenti in
enciclopedia. Ogni guida ha un titolo, una descrizione, un'icona (emoji), un
livello e una lista ordinata di articoli scelti dal catalogo.

USO:
    python gestisci_guide.py

Scrive su assets/js/guide.js usando lo stesso core robusto di data.js
(bitgen_data.py): scrittura atomica, backup con data/ora e validazione.
Il progresso di lettura dell'utente vive nel browser (localStorage) e NON
viene toccato da questo tool.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
import bitgen_data as bd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

GUIDE_FILE = SCRIPT_DIR / "assets" / "js" / "guide.js"
DATA_FILE = SCRIPT_DIR / "assets" / "js" / "data.js"
LIVELLI = ["Base", "Intermedio", "Avanzato"]


def colored(text, color):
    colors = {
        'green': '\033[92m', 'yellow': '\033[93m', 'red': '\033[91m',
        'blue': '\033[94m', 'bold': '\033[1m', 'dim': '\033[2m', 'end': '\033[0m',
    }
    return f"{colors.get(color, '')}{text}{colors['end']}"


def ask(prompt, default=None, required=False):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        v = input(colored(f"{prompt}{suffix}: ", 'yellow')).strip()
        if not v and default is not None:
            return default
        if v or not required:
            return v
        print(colored("Campo obbligatorio, riprova.", 'red'))


# ────────────────────────────────────────
# Dati
# ────────────────────────────────────────

def carica():
    guide = bd.leggi_guide(GUIDE_FILE) if GUIDE_FILE.exists() else []
    articoli = bd.leggi_articoli(DATA_FILE)
    idx = {bd.id_articolo(a): a for a in articoli}
    return guide, articoli, idx


def salva(guide):
    backup = bd.scrivi_guide(GUIDE_FILE, guide)
    print(colored("✓ guide.js salvato.", 'green')
          + (colored(f"  (backup: {backup.name})", 'dim') if backup else ""))


def titolo_articolo(idx, slug):
    a = idx.get(slug)
    return a.get('titolo') if a else colored(f"[MANCANTE: {slug}]", 'red')


# ────────────────────────────────────────
# Ricerca / scelta articoli
# ────────────────────────────────────────

def cerca(articoli, query):
    q = query.lower().strip()
    res = []
    for a in articoli:
        tit = a.get('titolo', '')
        if q in tit.lower() or q in a.get('rubrica', '').lower():
            res.append(a)
    return res


def aggiungi_articoli(guida, articoli, idx):
    print(colored("\nAggiungi articoli (cerca per parola nel titolo/rubrica).", 'blue'))
    print(colored("Comandi: scrivi una parola per cercare, 'fine' per terminare.", 'dim'))
    while True:
        q = input(colored("cerca> ", 'yellow')).strip()
        if not q or q.lower() in ('fine', 'q', 'stop'):
            break
        res = cerca(articoli, q)
        if not res:
            print(colored("  nessun risultato.", 'red'))
            continue
        res = res[:20]
        for i, a in enumerate(res, 1):
            gia = " (già presente)" if bd.id_articolo(a) in guida['articoli'] else ""
            print(f"  {i:2}. {a.get('titolo')}  {colored(a.get('rubrica',''),'dim')}{colored(gia,'green')}")
        sel = input(colored("numeri da aggiungere (es. 1,3,5) o Invio per nuova ricerca: ", 'yellow')).strip()
        if not sel:
            continue
        for tok in sel.replace(' ', '').split(','):
            if tok.isdigit() and 1 <= int(tok) <= len(res):
                slug = bd.id_articolo(res[int(tok) - 1])
                if slug not in guida['articoli']:
                    guida['articoli'].append(slug)
                    print(colored(f"  + {titolo_articolo(idx, slug)}", 'green'))
                else:
                    print(colored("  (già presente)", 'dim'))


def mostra_articoli_guida(guida, idx):
    if not guida['articoli']:
        print(colored("  (nessun articolo)", 'dim'))
        return
    for i, slug in enumerate(guida['articoli'], 1):
        print(f"  {i:2}. {titolo_articolo(idx, slug)}")


def rimuovi_articolo(guida, idx):
    mostra_articoli_guida(guida, idx)
    n = input(colored("numero da rimuovere (Invio per annullare): ", 'yellow')).strip()
    if n.isdigit() and 1 <= int(n) <= len(guida['articoli']):
        slug = guida['articoli'].pop(int(n) - 1)
        print(colored(f"  - rimosso: {titolo_articolo(idx, slug)}", 'green'))


def riordina(guida, idx):
    mostra_articoli_guida(guida, idx)
    a = input(colored("sposta il numero: ", 'yellow')).strip()
    b = input(colored("...alla posizione: ", 'yellow')).strip()
    if a.isdigit() and b.isdigit():
        ia, ib = int(a) - 1, int(b) - 1
        n = len(guida['articoli'])
        if 0 <= ia < n and 0 <= ib < n:
            slug = guida['articoli'].pop(ia)
            guida['articoli'].insert(ib, slug)
            print(colored("  ✓ riordinato.", 'green'))
            mostra_articoli_guida(guida, idx)


# ────────────────────────────────────────
# Editor di una singola guida
# ────────────────────────────────────────

def editor_guida(guida, articoli, idx, guide, nuova=False):
    while True:
        print()
        print(colored("=" * 60, 'green'))
        print(colored(f"  {guida.get('icona','📘')}  {guida.get('titolo','(senza titolo)')}", 'bold'))
        print(colored("=" * 60, 'green'))
        print(f"  Descrizione: {guida.get('descrizione','') or colored('(vuota)','dim')}")
        print(f"  Livello:     {guida.get('livello','Base')}   Icona: {guida.get('icona','📘')}")
        print(f"  Articoli:    {len(guida['articoli'])}")
        mostra_articoli_guida(guida, idx)
        print()
        print("  1. Rinomina titolo    2. Descrizione    3. Icona    4. Livello")
        print("  5. Aggiungi articoli  6. Rimuovi articolo    7. Riordina")
        print(colored("  8. Salva ed esci", 'green') + colored("     0. Annulla (scarta modifiche)", 'red'))
        scelta = input(colored("scelta: ", 'yellow')).strip()

        if scelta == '1':
            guida['titolo'] = ask("Nuovo titolo", default=guida.get('titolo', ''), required=True)
        elif scelta == '2':
            guida['descrizione'] = ask("Descrizione", default=guida.get('descrizione', ''))
        elif scelta == '3':
            guida['icona'] = ask("Icona (emoji)", default=guida.get('icona', '📘'))
        elif scelta == '4':
            print("  " + "  ".join(f"{i}.{l}" for i, l in enumerate(LIVELLI, 1)))
            s = input(colored("numero livello: ", 'yellow')).strip()
            if s.isdigit() and 1 <= int(s) <= len(LIVELLI):
                guida['livello'] = LIVELLI[int(s) - 1]
        elif scelta == '5':
            aggiungi_articoli(guida, articoli, idx)
        elif scelta == '6':
            rimuovi_articolo(guida, idx)
        elif scelta == '7':
            riordina(guida, idx)
        elif scelta == '8':
            if not guida.get('titolo'):
                print(colored("Serve almeno un titolo.", 'red'))
                continue
            if not guida.get('id'):
                guida['id'] = bd.slugify(guida['titolo'])
            if nuova:
                guide.append(guida)
            salva(guide)
            return True
        elif scelta == '0':
            print(colored("Modifiche scartate.", 'red'))
            return False


# ────────────────────────────────────────
# Menu principale
# ────────────────────────────────────────

def main():
    if not DATA_FILE.exists():
        print(colored(f"✗ Non trovo {DATA_FILE}", 'red'))
        return
    while True:
        guide, articoli, idx = carica()
        print()
        print(colored("=" * 60, 'green'))
        print(colored("  BItGen - Gestore Guide", 'bold'))
        print(colored("=" * 60, 'green'))
        if not guide:
            print(colored("  (nessuna guida ancora)", 'dim'))
        for i, g in enumerate(guide, 1):
            p = f"{len(g.get('articoli', []))} art."
            print(f"  {i:2}. {g.get('icona','📘')} {g.get('titolo')}  "
                  + colored(f"[{g.get('livello','Base')} · {p}]", 'dim'))
        print()
        print(colored("  n", 'green') + ". Nuova guida    "
              + colored("<numero>", 'green') + ". Modifica    "
              + colored("e<numero>", 'red') + ". Elimina    "
              + colored("q", 'yellow') + ". Esci")
        scelta = input(colored("scelta: ", 'yellow')).strip().lower()

        if scelta in ('q', 'quit', 'esci', ''):
            print(colored("A presto!", 'blue'))
            return
        elif scelta == 'n':
            nuova = {"titolo": "", "descrizione": "", "icona": "📘",
                     "livello": "Base", "articoli": []}
            nuova['titolo'] = ask("Titolo della guida", required=True)
            nuova['descrizione'] = ask("Descrizione (una frase)")
            nuova['icona'] = ask("Icona (emoji)", default="📘")
            print("  " + "  ".join(f"{i}.{l}" for i, l in enumerate(LIVELLI, 1)))
            s = input(colored("numero livello [1]: ", 'yellow')).strip() or "1"
            if s.isdigit() and 1 <= int(s) <= len(LIVELLI):
                nuova['livello'] = LIVELLI[int(s) - 1]
            aggiungi_articoli(nuova, articoli, idx)
            editor_guida(nuova, articoli, idx, guide, nuova=True)
        elif scelta.startswith('e') and scelta[1:].isdigit():
            n = int(scelta[1:])
            if 1 <= n <= len(guide):
                g = guide[n - 1]
                conf = input(colored(f"Eliminare «{g.get('titolo')}»? [s/N]: ", 'red')).strip().lower()
                if conf in ('s', 'si', 'y', 'yes'):
                    guide.pop(n - 1)
                    salva(guide)
        elif scelta.isdigit():
            n = int(scelta)
            if 1 <= n <= len(guide):
                editor_guida(guide[n - 1], articoli, idx, guide, nuova=False)
        else:
            print(colored("Comando non riconosciuto.", 'red'))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n\nInterrotto.", 'yellow'))
        sys.exit(0)
