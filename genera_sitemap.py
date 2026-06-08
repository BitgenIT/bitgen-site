#!/usr/bin/env python3
"""
BItGen - Generatore sitemap.xml e robots.txt per SEO
====================================================

USO:
    python3 genera_sitemap.py

Legge gli articoli da assets/js/data.js ed estrae i dati necessari
per generare il sitemap.xml completo e il robots.txt.

Esegui questo script ogni volta che aggiungi nuovi articoli,
prima di ri-caricare il sito sull'hosting.
"""

import re
from pathlib import Path
from datetime import datetime


SCRIPT_DIR = Path(__file__).parent
DATA_FILE = SCRIPT_DIR / "assets" / "js" / "data.js"
CONFIG_FILE = SCRIPT_DIR / "assets" / "js" / "config.js"


def estrai_url_sito():
    """Legge l'URL del sito dal config.js"""
    if not CONFIG_FILE.exists():
        return "https://bitgen.it"
    testo = CONFIG_FILE.read_text(encoding='utf-8')
    match = re.search(r'url:\s*["\']([^"\']+)["\']', testo)
    return match.group(1) if match else "https://bitgen.it"


def slugify(text):
    """Genera slug URL-friendly (corrispondente alla funzione JS)"""
    import unicodedata
    text = text.lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    text = re.sub(r'-+', '-', text)
    return text[:60]


def estrai_articoli():
    """Estrae gli articoli dal file data.js"""
    if not DATA_FILE.exists():
        print(f"✗ File non trovato: {DATA_FILE}")
        return []
    
    testo = DATA_FILE.read_text(encoding='utf-8')
    
    # Cerca tutti i blocchi articolo
    articoli = []
    # Pattern per individuare titolo e data di ogni articolo
    pattern = r'\{\s*titolo:\s*["\']([^"\']+)["\'][^}]*?(?:data:\s*["\']([^"\']+)["\'])?[^}]*?\}'
    
    # Metodo alternativo più robusto: splitta per "titolo:" e analizza ogni blocco
    blocchi = re.split(r'(?=\n\s+titolo:)', testo)
    
    for blocco in blocchi:
        titolo_match = re.search(r'titolo:\s*["\']([^"\']+)["\']', blocco)
        if not titolo_match:
            continue
        titolo = titolo_match.group(1)
        
        data_match = re.search(r'data:\s*["\']([^"\']+)["\']', blocco)
        data = data_match.group(1) if data_match else datetime.now().strftime('%Y-%m-%d')
        
        id_match = re.search(r'id:\s*["\']([^"\']+)["\']', blocco)
        id_articolo = id_match.group(1) if id_match else slugify(titolo)
        
        articoli.append({
            'id': id_articolo,
            'titolo': titolo,
            'data': data
        })
    
    return articoli


def genera_sitemap(url_base, articoli):
    """Genera sitemap.xml"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Pagine statiche
    pagine = [
        ('/', '1.0', 'daily'),
        ('/enciclopedia.html', '0.9', 'daily'),
        ('/contatti.html', '0.5', 'monthly'),
    ]
    
    for path, priority, freq in pagine:
        xml += '  <url>\n'
        xml += f'    <loc>{url_base}{path}</loc>\n'
        xml += f'    <lastmod>{today}</lastmod>\n'
        xml += f'    <changefreq>{freq}</changefreq>\n'
        xml += f'    <priority>{priority}</priority>\n'
        xml += '  </url>\n'
    
    # Articoli
    for art in articoli:
        xml += '  <url>\n'
        xml += f'    <loc>{url_base}/articolo.html?id={art["id"]}</loc>\n'
        xml += f'    <lastmod>{art["data"]}</lastmod>\n'
        xml += '    <changefreq>weekly</changefreq>\n'
        xml += '    <priority>0.8</priority>\n'
        xml += '  </url>\n'
    
    xml += '</urlset>\n'
    return xml


def genera_robots(url_base):
    """Genera robots.txt"""
    return f"""User-agent: *
Allow: /

Sitemap: {url_base}/sitemap.xml

# Blocca accesso a file di configurazione
Disallow: /assets/js/config.js
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
    
    # Genera sitemap
    sitemap_content = genera_sitemap(url_base, articoli)
    sitemap_path = SCRIPT_DIR / "sitemap.xml"
    sitemap_path.write_text(sitemap_content, encoding='utf-8')
    print(f"✓ Sitemap generato: {sitemap_path.name}")
    
    # Genera robots.txt
    robots_content = genera_robots(url_base)
    robots_path = SCRIPT_DIR / "robots.txt"
    robots_path.write_text(robots_content, encoding='utf-8')
    print(f"✓ Robots.txt generato: {robots_path.name}")
    
    print()
    print("Prossimi passi per la SEO:")
    print(f"  1. Ricarica il sito sul tuo hosting")
    print(f"  2. Vai su Google Search Console: https://search.google.com/search-console")
    print(f"  3. Aggiungi il tuo sito come proprietà")
    print(f"  4. Invia il sitemap: {url_base}/sitemap.xml")
    print()


if __name__ == "__main__":
    main()
