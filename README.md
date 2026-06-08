# 🟢 BItGen — Sito v2

Sito web ufficiale di BItGen con integrazioni Analytics, SEO e Newsletter.

---

## 🆕 Cosa c'è di nuovo nella v2

- ✅ **Google Analytics** integrato (basta inserire il Measurement ID)
- ✅ **SEO dinamico** con meta tag, Open Graph, Twitter Card e Schema.org
- ✅ **Newsletter** con supporto multi-provider (Formspree/Mailchimp/Brevo/Substack)
- ✅ **Gestore articoli** via script Python interattivo
- ✅ **Generatore sitemap** automatico
- ✅ **Calcolo automatico** di durata, estratto, slug, tag per ogni articolo
- ✅ **Tracking eventi** (ricerche, letture articoli, iscrizioni newsletter)

---

## 📁 Struttura

```
bitgen_site/
├── index.html              ← Home page
├── enciclopedia.html       ← Tutti i contenuti
├── articolo.html           ← Pagina singolo articolo
├── contatti.html           ← Contatti + FAQ
├── aggiungi_articolo.py    ← 🆕 Script per aggiungere articoli
├── genera_sitemap.py       ← 🆕 Generatore sitemap.xml
├── sitemap.xml             ← Generato da genera_sitemap.py
├── robots.txt              ← Generato da genera_sitemap.py
└── assets/
    ├── css/style.css
    ├── js/
    │   ├── config.js       ← ⭐ FILE DI CONFIGURAZIONE CENTRALE
    │   ├── data.js         ← Database articoli
    │   └── main.js         ← Logica app
    └── images/logo.png
```

---

## ⚡ Quick Start (20 minuti totali)

### 1. Personalizza il sito (5 min)

Apri `assets/js/config.js` e modifica:
- `site.url` → il tuo dominio
- `site.email` → la tua email
- `social.*` → i link ai tuoi canali

### 2. Attiva Google Analytics (10 min)

1. Crea account su https://analytics.google.com
2. Copia il Measurement ID (formato `G-XXXXXXXXXX`)
3. In `config.js`: `enabled: true` e incolla l'ID

### 3. Attiva Newsletter con Formspree (5 min)

1. Registrati su https://formspree.io (gratis)
2. Crea un form, copia l'endpoint
3. In `config.js`: incolla l'endpoint in `formspreeEndpoint`

### 4. Genera sitemap

```bash
python3 genera_sitemap.py
```

### 5. Pubblica su Netlify

Trascina la cartella su https://app.netlify.com/drop → sito online in 30 secondi.

---

## 📝 Aggiungere un articolo

### Metodo interattivo

```bash
python3 aggiungi_articolo.py
```

Lo script ti guida con 4 domande e calcola automaticamente durata, estratto, tag, slug.

### Metodo manuale

Apri `assets/js/data.js` e aggiungi nell'array `articoliGrezzi`:

```javascript
{
  titolo: "Il tuo titolo",
  rubrica: "Ma cos'è?",
  videoUrl: "https://youtube.com/watch?v=...",
  contenuto: `Testo completo dell'articolo.

TITOLO IN MAIUSCOLO
Diventa un sottotitolo automaticamente.

Continua scrivendo.`
},
```

Tutto il resto viene generato in automatico.

---

## 📖 Guida completa

**Apri il file `BItGen_Guida_Configurazioni_v2.docx`** per la guida dettagliata con screenshot e procedure passo-passo per:

- Google Analytics (setup completo)
- SEO (Search Console, sitemap, best practice)
- Newsletter (Formspree + alternative avanzate)
- Gestione articoli (script Python e workflow)
- Pubblicazione (Netlify, dominio, HTTPS)
- Checklist finale pre-lancio

---

© 2026 BItGen
