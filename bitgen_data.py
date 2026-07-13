#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BItGen - Core dati condiviso
============================

Lettura e scrittura ROBUSTA dell'array `articoliGrezzi` dentro data.js.

A differenza del vecchio parsing a regex, qui:
  - l'array è in formato JSON e viene letto con json.JSONDecoder().raw_decode,
    quindi nessun carattere speciale (apostrofi, backtick, graffe, a-capo) può
    rompere il parsing;
  - TUTTI i campi di ogni articolo vengono preservati (anche quelli che non
    conosciamo): niente più perdita silenziosa di id/estratto/thumbnail;
  - la scrittura è ATOMICA (file temporaneo + replace) e crea backup con data/ora;
  - dopo la scrittura il risultato viene ri-letto e validato (conteggio articoli).

Importato da genera_sitemap.py e aggiungi_articolo.py. La stessa logica è
replicata (in forma autonoma) dentro bitgen_manager.py, che resta un file unico.
"""

import os
import re
import json
import unicodedata
from datetime import datetime
from pathlib import Path

ARRAY_NAME = "articoliGrezzi"
GUIDE_ARRAY = "guideGrezze"
MAX_BACKUP = 15  # quanti backup tenere


def slugify(text):
    """Genera lo slug/id URL-friendly. Identica alla slugify() lato JS in data.js."""
    text = (text or "").lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text[:60]


def data_oggi():
    return datetime.now().strftime('%Y-%m-%d')


def id_articolo(art):
    """Id come lo calcola il frontend: campo 'id' se presente, altrimenti slug del titolo."""
    return art.get('id') or slugify(art.get('titolo', ''))


def estrae_estratto(contenuto, max_length=180):
    """Estratto dalle prime frasi utili. Parità con estraeEstratto() in data.js."""
    blocchi = re.split(r'\n\s*\n', contenuto or "")
    testo = ''
    for blocco in blocchi:
        trimmed = blocco.strip()
        if not trimmed:
            continue
        if re.match(r'^\[IMG:', trimmed, re.IGNORECASE):
            continue
        if len(trimmed) < 80 and trimmed == trimmed.upper():
            continue
        testo = trimmed
        break
    if not testo:
        testo = (contenuto or "").strip()
    if len(testo) <= max_length:
        return testo
    truncated = testo[:max_length]
    last_dot = truncated.rfind('.')
    last_space = truncated.rfind(' ')
    cut = last_dot + 1 if last_dot > 50 else last_space
    return testo[:cut].strip() + ('…' if cut < len(testo) else '')


def estratto_articolo(art):
    """Estratto come lo calcola il frontend: campo esplicito, poi breve, poi approfondito."""
    if art.get('estratto'):
        return art['estratto']
    base = art.get('contenutoBreve') or art.get('contenuto') or ''
    return estrae_estratto(base)


def _individua_array(testo, nome=ARRAY_NAME):
    """Trova gli indici [start, end) del literal array JSON dopo 'const <nome> ='.

    Ritorna (parsed_list, start_bracket, end_after_bracket).
    Solleva ValueError se non trova un array JSON valido.
    """
    m = re.search(r'\b' + re.escape(nome) + r'\s*=\s*', testo)
    if not m:
        raise ValueError(f"Non trovo '{nome} = ...' nel file")
    start = testo.find('[', m.end())
    if start == -1:
        raise ValueError(f"Non trovo l'inizio dell'array '[' per {nome}")
    try:
        dati, end = json.JSONDecoder().raw_decode(testo, start)
    except json.JSONDecodeError as e:
        raise ValueError(f"L'array {nome} non è JSON valido: {e}")
    if not isinstance(dati, list):
        raise ValueError(f"Il valore di {nome} non è una lista")
    return dati, start, end


def leggi_articoli(data_js_path):
    """Ritorna la lista di articoli (dict) letti da data.js, nell'ordine del file."""
    testo = Path(data_js_path).read_text(encoding='utf-8')
    articoli, _, _ = _individua_array(testo)
    return articoli


def _pulisci_articolo(art):
    """Rimuove i campi calcolati a runtime e i campi vuoti, mantenendo l'ordine utile.

    Salviamo solo i dati 'sorgente'; id/estratto/durata/hasBreve sono ricalcolati
    dal frontend, quindi non li persistiamo a meno che siano stati impostati a mano.
    """
    campi_runtime = {'hasBreve', 'hasTecnico'}
    ordine = ['titolo', 'rubrica', 'data', 'videoUrl', 'thumbnail',
              'tags', 'correlati', 'id', 'estratto', 'durata', 'contenutoBreve', 'contenuto', 'contenutoTecnico']
    out = {}
    for k in ordine:
        if k in art and k not in campi_runtime:
            v = art[k]
            # non scrivere stringhe vuote / None / liste vuote (restano default lato JS)
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == '':
                continue
            if isinstance(v, list) and len(v) == 0:
                continue
            out[k] = v
    # eventuali campi extra non previsti: preservali comunque (no perdita dati)
    for k, v in art.items():
        if k not in out and k not in campi_runtime:
            out[k] = v
    return out


def _backup(path):
    """Crea un backup timestampato e mantiene solo gli ultimi MAX_BACKUP."""
    path = Path(path)
    if not path.exists():
        return None
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = path.with_name(path.name + f'.{ts}.bak')
    backup.write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
    # prune
    vecchi = sorted(path.parent.glob(path.name + '.*.bak'))
    for b in vecchi[:-MAX_BACKUP]:
        try:
            b.unlink()
        except OSError:
            pass
    return backup


def _scrivi_array(js_path, items, nome, pulisci):
    """Riscrive l'array <nome> nel file JS in modo atomico e validato.

    `pulisci` è una funzione che normalizza un singolo elemento prima della
    scrittura. Ritorna il Path del backup creato. Solleva ValueError se la
    validazione fallisce (in tal caso il file ORIGINALE non viene toccato).
    """
    path = Path(js_path)
    testo = path.read_text(encoding='utf-8')
    _, start, end = _individua_array(testo, nome)

    puliti = [pulisci(a) for a in items]
    nuovo_json = json.dumps(puliti, ensure_ascii=False, indent=2)
    nuovo_testo = testo[:start] + nuovo_json + testo[end:]

    # VALIDAZIONE pre-scrittura: ri-parsa il risultato e verifica il conteggio
    ricontrollo, _, _ = _individua_array(nuovo_testo, nome)
    if len(ricontrollo) != len(puliti):
        raise ValueError(
            f"Validazione fallita: attesi {len(puliti)} elementi, "
            f"riletti {len(ricontrollo)}. Il file NON è stato modificato.")

    backup = _backup(path)

    # scrittura ATOMICA: file temporaneo nello stesso folder + replace
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(nuovo_testo, encoding='utf-8')
    os.replace(str(tmp), str(path))
    return backup


def scrivi_articoli(data_js_path, articoli):
    """Riscrive l'array articoli in data.js in modo atomico e validato."""
    return _scrivi_array(data_js_path, articoli, ARRAY_NAME, _pulisci_articolo)


# ────────────────────────────────────────
# GUIDE (percorsi di lettura) — assets/js/guide.js
# ────────────────────────────────────────

def _pulisci_guida(g):
    """Normalizza una guida: ordina i campi noti, scarta i vuoti, preserva gli extra."""
    ordine = ['titolo', 'descrizione', 'icona', 'livello', 'articoli', 'id']
    out = {}
    for k in ordine:
        if k in g:
            v = g[k]
            if v is None:
                continue
            if isinstance(v, str) and v.strip() == '':
                continue
            if isinstance(v, list) and len(v) == 0:
                # 'articoli' vuoto è ammesso (guida in costruzione)
                if k == 'articoli':
                    out[k] = []
                continue
            out[k] = v
    for k, v in g.items():
        if k not in out:
            out[k] = v
    return out


def id_guida(g):
    """Id/slug di una guida: campo 'id' se presente, altrimenti slug del titolo."""
    return g.get('id') or slugify(g.get('titolo', ''))


def leggi_guide(guide_js_path):
    """Ritorna la lista di guide (dict) lette da guide.js, nell'ordine del file."""
    testo = Path(guide_js_path).read_text(encoding='utf-8')
    guide, _, _ = _individua_array(testo, GUIDE_ARRAY)
    return guide


def scrivi_guide(guide_js_path, guide):
    """Riscrive l'array guide in guide.js in modo atomico e validato."""
    return _scrivi_array(guide_js_path, guide, GUIDE_ARRAY, _pulisci_guida)
