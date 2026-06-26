#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BItGen - Generatore sitemap.xml e robots.txt per SEO
====================================================

USO:
    python3 genera_sitemap.py

Legge gli articoli da assets/js/data.js (formato JSON) tramite il core condiviso
bitgen_data.py: lo stesso parser e la stessa slugify usati dal Gestore Articoli,
quindi gli id nella sitemap coincidono SEMPRE con quelli reali del sito (niente
più troncamento dei titoli con apostrofo).

Esegui questo script ogni volta che aggiungi nuovi articoli, prima di ri-caricare
il sito sull'hosting.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape
from urllib.parse import quote

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
import bitgen_data as bd
import genera_pagine

DATA_FILE = SCRIPT_DIR / "assets" / "js" / "data.js"
CONFIG_FILE = SCRIPT_DIR / "assets" / "js" / "config.js"

try:
    sys.stdout.reconfigure(encoding="utf-8")  # evita errori sui simboli su Windows
except Exception:
    pass


def estrai_url_sito():
    """Legge l'URL del sito dal config.js."""
    if not CONFIG_FILE.exists():
        return "https://bitgen.it"
    testo = CONFIG_FILE.read_text(encoding="utf-8")
    match = re.search(r'url:\s*["\']([^"\']+)["\']', testo)
    return match.group(1) if match else "https://bitgen.it"


def estrai_articoli():
    """Estrae (id, titolo, data) di ogni articolo usando il core condiviso."""
    if not DATA_FILE.exists():
        print(f"✗ File non trovato: {DATA_FILE}")
        return []
    try:
        articoli = bd.leggi_articoli(DATA_FILE)
    except Exception as e:
        print(f"✗ Errore lettura data.js: {e}")
        return []
    out = []
    for a in articoli:
        out.append({
            "id": bd.id_articolo(a),
            "titolo": a.get("titolo", ""),
            "rubrica": a.get("rubrica", ""),
            "data": a.get("data") or bd.data_oggi(),
        })
    return out


def genera_sitemap(url_base, articoli):
    """Genera sitemap.xml."""
    today = bd.data_oggi()

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    pagine = [
        ('/', '1.0', 'daily'),
        ('/enciclopedia.html', '0.9', 'daily'),
        ('/contatti.html', '0.5', 'monthly'),
        ('/privacy.html', '0.2', 'yearly'),
    ]
    for path, priority, freq in pagine:
        xml += '  <url>\n'
        xml += f'    <loc>{xml_escape(url_base + path)}</loc>\n'
        xml += f'    <lastmod>{today}</lastmod>\n'
        xml += f'    <changefreq>{freq}</changefreq>\n'
        xml += f'    <priority>{priority}</priority>\n'
        xml += '  </url>\n'

    for art in articoli:
        loc = f'{url_base}/{genera_pagine.percorso_articolo(art)}'
        xml += '  <url>\n'
        xml += f'    <loc>{xml_escape(loc)}</loc>\n'
        xml += f'    <lastmod>{art["data"]}</lastmod>\n'
        xml += '    <changefreq>weekly</changefreq>\n'
        xml += '    <priority>0.8</priority>\n'
        xml += '  </url>\n'

    xml += '</urlset>\n'
    return xml


def genera_robots(url_base):
    """Genera robots.txt."""
    return f"""User-agent: *
Allow: /

Sitemap: {url_base}/sitemap.xml
"""


def main():
    print("=" * 60)
    print("  BItGen - Generatore Sitemap e Robots")
    print("=" * 60)
    print()

    url_base = estrai_url_sito().rstrip('/')
    print(f"URL base: {url_base}")

    articoli = estrai_articoli()
    print(f"Articoli trovati: {len(articoli)}")

    sitemap_content = genera_sitemap(url_base, articoli)
    sitemap_path = SCRIPT_DIR / "sitemap.xml"
    sitemap_path.write_text(sitemap_content, encoding='utf-8')
    print(f"✓ Sitemap generato: {sitemap_path.name}")

    robots_content = genera_robots(url_base)
    robots_path = SCRIPT_DIR / "robots.txt"
    robots_path.write_text(robots_content, encoding='utf-8')
    print(f"✓ Robots.txt generato: {robots_path.name}")

    # Pagine articolo statiche (anteprime social + SEO)
    try:
        articoli_full = bd.leggi_articoli(DATA_FILE)
        generati, rimossi = genera_pagine.genera_pagine(SCRIPT_DIR, articoli_full, url_base)
        print(f"✓ Pagine articolo generate: {len(generati)}"
              + (f" (rimosse {rimossi} obsolete)" if rimossi else ""))
    except Exception as e:
        print(f"✗ Errore generazione pagine articolo: {e}")

    print()
    print("Prossimi passi per la SEO:")
    print("  1. Ricarica il sito sul tuo hosting")
    print("  2. Vai su Google Search Console: https://search.google.com/search-console")
    print("  3. Aggiungi il tuo sito come proprietà")
    print(f"  4. Invia il sitemap: {url_base}/sitemap.xml")
    print()


if __name__ == "__main__":
    main()
