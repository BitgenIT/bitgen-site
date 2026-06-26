#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BItGen - Generatore pagine articolo statiche (per anteprime social e SEO)
=========================================================================

Per OGNI articolo crea una pagina HTML a sé (es. cose-il-cloud.html) partendo
dal template articolo.html, con i meta "cotti" nell'HTML:
  - <title>, description, Open Graph (og:title/description/image/url), Twitter Card,
    canonical e dati strutturati JSON-LD specifici dell'articolo.

Così quando condividi il link su WhatsApp/Facebook/Telegram (che NON eseguono
JavaScript) l'anteprima mostra titolo e immagine GIUSTI dell'articolo.

Il corpo dell'articolo viene comunque renderizzato dallo stesso main.js (un solo
motore di rendering), tramite window.__ARTICLE_ID__; per chi non ha JavaScript
c'è un fallback <noscript> con titolo ed estratto.

Le pagine generate contengono il marcatore BITGEN-AUTO-GENERATED: a ogni esecuzione
quelle non più corrispondenti a un articolo vengono rimosse (cleanup automatico).
"""

import re
import sys
import json
import html
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
import bitgen_data as bd

TEMPLATE = SCRIPT_DIR / "articolo.html"
MARKER = "<!-- BITGEN-AUTO-GENERATED -->"
RISERVATI = {"index", "enciclopedia", "contatti", "articolo", "404", "sitemap", "robots"}

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def nome_file(slug):
    if slug in RISERVATI:
        slug = "articolo-" + slug
    return slug + ".html"


def costruisci_pagina(template, art, url_base):
    slug = bd.id_articolo(art)
    titolo = art.get("titolo", "")
    estratto = bd.estratto_articolo(art)
    data = art.get("data", "") or bd.data_oggi()
    rubrica = art.get("rubrica", "")
    tags = art.get("tags", []) or []

    url = f"{url_base}/{nome_file(slug)}"
    if art.get("thumbnail"):
        img_abs = f"{url_base}/{art['thumbnail']}"
    else:
        img_abs = f"{url_base}/assets/images/logo.png"

    full_title = f"{titolo} — BItGen"
    e = lambda s: html.escape(str(s), quote=True)

    social = (
        f'<meta property="og:image" content="{e(img_abs)}">\n'
        f'<meta property="og:title" content="{e(full_title)}">\n'
        f'<meta property="og:description" content="{e(estratto)}">\n'
        f'<meta property="og:url" content="{e(url)}">\n'
        f'<meta property="og:site_name" content="BItGen">\n'
        f'<meta property="og:locale" content="it_IT">\n'
        f'<meta property="article:published_time" content="{e(data)}">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{e(full_title)}">\n'
        f'<meta name="twitter:description" content="{e(estratto)}">\n'
        f'<meta name="twitter:image" content="{e(img_abs)}">\n'
        f'<link rel="canonical" href="{e(url)}">'
    )

    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": titolo,
        "description": estratto,
        "image": img_abs,
        "author": {"@type": "Organization", "name": "BItGen", "url": url_base},
        "publisher": {
            "@type": "Organization",
            "name": "BItGen",
            "logo": {"@type": "ImageObject", "url": f"{url_base}/assets/images/logo.png"},
        },
        "datePublished": data,
        "dateModified": data,
        "articleSection": rubrica,
        "keywords": ", ".join(tags),
        "inLanguage": "it",
        "mainEntityOfPage": url,
    }
    jsonld = ('<script type="application/ld+json">'
              + json.dumps(ld, ensure_ascii=False) + '</script>\n</head>')

    noscript = (
        '<article class="article-page" id="articolo-container">'
        '<noscript><div class="container" style="padding:2rem 0">'
        f'<p><a href="enciclopedia.html">← Enciclopedia</a></p>'
        f'<h1>{e(titolo)}</h1><p>{e(estratto)}</p>'
        '<p>Attiva JavaScript per leggere l\'articolo completo.</p>'
        '</div></noscript></article>'
    )

    page = template
    page = page.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n" + MARKER, 1)
    page = page.replace("<title>Articolo — BItGen</title>",
                        f"<title>{e(full_title)}</title>", 1)
    page = page.replace(
        '<meta name="description" content="Leggi l\'articolo completo del video BItGen.">',
        f'<meta name="description" content="{e(estratto)}">', 1)
    page = page.replace(
        '<meta property="og:image" content="assets/images/logo.png">', social, 1)
    page = page.replace("</head>", jsonld, 1)
    page = page.replace(
        '<script src="assets/js/config.js"></script>',
        f'<script>window.__ARTICLE_ID__ = {json.dumps(slug)};</script>\n'
        '<script src="assets/js/config.js"></script>', 1)
    page = page.replace(
        '<article class="article-page" id="articolo-container"></article>',
        noscript, 1)
    return slug, page


def genera_pagine(site_dir, articoli, url_base):
    site_dir = Path(site_dir)
    template = (site_dir / "articolo.html").read_text(encoding="utf-8")
    url_base = url_base.rstrip("/")

    generati = set()
    for art in articoli:
        if not art.get("titolo"):
            continue
        slug, page = costruisci_pagina(template, art, url_base)
        fname = nome_file(slug)
        (site_dir / fname).write_text(page, encoding="utf-8")
        generati.add(fname)

    # cleanup: rimuovi vecchie pagine generate non più corrispondenti ad alcun articolo
    rimossi = 0
    for f in site_dir.glob("*.html"):
        if f.name in generati:
            continue
        try:
            testo = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if MARKER in testo:
            f.unlink()
            rimossi += 1

    return generati, rimossi


def _url_base_da_config(site_dir):
    cfg = Path(site_dir) / "assets" / "js" / "config.js"
    if cfg.exists():
        m = re.search(r'url:\s*["\']([^"\']+)["\']', cfg.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return "https://bitgen.it"


def main():
    articoli = bd.leggi_articoli(SCRIPT_DIR / "assets" / "js" / "data.js")
    url_base = _url_base_da_config(SCRIPT_DIR)
    generati, rimossi = genera_pagine(SCRIPT_DIR, articoli, url_base)
    print(f"✓ Pagine articolo generate: {len(generati)}")
    if rimossi:
        print(f"✓ Pagine obsolete rimosse: {rimossi}")


if __name__ == "__main__":
    main()
