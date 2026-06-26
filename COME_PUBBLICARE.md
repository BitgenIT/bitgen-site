# 🚀 Come pubblicare gli aggiornamenti (GitHub Desktop)

Guida rapida per mettere online un articolo nuovo o una modifica.

---

## Domanda: "Quali file devo caricare?"

**Risposta breve: non li scegli tu, uno per uno.** GitHub Desktop **rileva da solo
TUTTI i file cambiati** e li carica insieme. Tu devi solo confermare (Commit) e
inviare (Push). Non serve sapere quali file sono cambiati.

Per curiosità, quando aggiungi un articolo dal Gestore cambiano di solito:
- `assets/js/data.js` (il testo dell'articolo)
- `assets/images/...` (le immagini nuove che hai caricato)
- `enciclopedia/<rubrica>/<slug>.html` (la pagina dell'articolo, generata da sola)
- `sitemap.xml` e `robots.txt` (per Google)

Sono tutti dentro la cartella del sito, quindi GitHub Desktop li vede tutti.

---

## Passo passo

1. **Aggiungi/modifica l'articolo** con il Gestore (`bitgen_manager.py`) e salva.
   Al salvataggio le pagine e la sitemap si aggiornano da sole.

2. **Apri GitHub Desktop.** A sinistra, nella scheda **"Changes"**, vedrai l'elenco
   di tutti i file modificati (con la spunta ✓ già messa). Va bene così: lasciali
   tutti spuntati.

3. In basso a sinistra, nel riquadro **"Summary"**, scrivi una frase breve, es.
   *"Nuovo articolo: Cos'è il Cloud"*.

4. Premi il pulsante blu **"Commit to main"** (o "Commit to master").

5. In alto compare **"Push origin"**: premilo. (In alternativa menu
   *Repository → Push*.)

6. Aspetta 30–60 secondi: GitHub Pages ricostruisce il sito ed è online. ✅

---

## Suggerimenti

- **Prima di pubblicare**, controlla l'articolo con il pulsante
  **"👁 Anteprima nel browser"** nel Gestore: lo vedi esattamente come apparirà.
- Se dopo la pubblicazione vedi ancora la versione vecchia, fai un **ricarica
  forzato** del browser: **Ctrl + F5** (Windows). È solo la cache del browser.
- Non serve cancellare niente a mano: gli articoli eliminati e le loro pagine
  vengono rimossi in automatico al salvataggio successivo.
