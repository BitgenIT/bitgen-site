#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BItGen - Generatore pagine articolo statiche (per anteprime social e SEO)
=========================================================================

Per OGNI articolo crea una pagina HTML a sé dentro una struttura ordinata:

    enciclopedia/<rubrica>/<slug>.html
    es.  enciclopedia/ma-cos-e/cose-il-cloud.html

così la cartella principale del sito resta pulita. Ogni pagina ha i meta
"cotti" nell'HTML (Open Graph, Twitter Card, canonical, JSON-LD) per le
anteprime social di WhatsApp/Facebook (che NON eseguono JavaScript).

Le pagine stanno in sottocartelle: un tag <base href="../../"> fa sì che CSS,
JS, immagini e link continuino a funzionare come se la pagina fosse nella radice.

Il corpo dell'articolo è reso dallo stesso main.js (un solo motore) tramite
window.__ARTICLE_ID__; per chi non ha JavaScript c'è un fallback <noscript>.

Le pagine generate contengono il marcatore BITGEN-AUTO-GENERATED: a ogni
esecuzione quelle non più corrispondenti a un articolo vengono rimosse.
"""

import re
import sys
import json
import html
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
import bitgen_data as bd

MARKER = "<!-- BITGEN-AUTO-GENERATED -->"
ENC_DIR = "enciclopedia"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def rubrica_slug(rubrica):
    return bd.slugify(rubrica) or "altro"


def percorso_articolo(art):
    """Percorso relativo della pagina di un articolo (con / come separatore)."""
    return f"{ENC_DIR}/{rubrica_slug(art.get('rubrica', ''))}/{bd.id_articolo(art)}.html"


def costruisci_pagina(template, art, url_base):
    slug = bd.id_articolo(art)
    titolo = art.get("titolo", "")
    estratto = bd.estratto_articolo(art)
    data = art.get("data", "") or bd.data_oggi()
    rubrica = art.get("rubrica", "")
    tags = art.get("tags", []) or []

    rel = percorso_articolo(art)
    url = f"{url_base}/{rel}"
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
        '<p><a href="enciclopedia.html">← Enciclopedia</a></p>'
        f'<h1>{e(titolo)}</h1><p>{e(estratto)}</p>'
        '<p>Attiva JavaScript per leggere l\'articolo completo.</p>'
        '</div></noscript></article>'
    )

    page = template
    page = page.replace("<!DOCTYPE html>", "<!DOCTYPE html>\n" + MARKER, 1)
    # <base> per far funzionare percorsi relativi da dentro le sottocartelle
    page = page.replace(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<base href="../../">', 1)
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
    return rel, page


def genera_pagine(site_dir, articoli, url_base):
    site_dir = Path(site_dir)
    template = (site_dir / "articolo.html").read_text(encoding="utf-8")
    url_base = url_base.rstrip("/")

    generati = set()
    for art in articoli:
        if not art.get("titolo"):
            continue
        rel, page = costruisci_pagina(template, art, url_base)
        out = site_dir / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page, encoding="utf-8")
        generati.add(rel)

    # cleanup: rimuovi vecchie pagine generate (anche quelle nella radice della v
    # precedente) non più corrispondenti ad alcun articolo
    candidati = list(site_dir.glob("*.html"))
    enc = site_dir / ENC_DIR
    if enc.exists():
        candidati += list(enc.rglob("*.html"))
    rimossi = 0
    for f in candidati:
        rel = f.relative_to(site_dir).as_posix()
        if rel in generati:
            continue
        try:
            testo = f.read_text(encoding="utf-8")
        except OSError:
            continue
        if MARKER in testo:
            f.unlink()
            rimossi += 1

    # rimuovi eventuali sottocartelle rubrica rimaste vuote
    if enc.exists():
        for d in sorted(enc.glob("*"), reverse=True):
            if d.is_dir():
                try:
                    next(d.iterdir())
                except StopIteration:
                    d.rmdir()

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
