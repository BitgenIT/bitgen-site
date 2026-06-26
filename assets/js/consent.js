// ============================================
// BITGEN - GESTIONE CONSENSO COOKIE (self-hosted, senza limiti di pagine)
// ============================================
//
// Sostituisce Cookiebot. Mostra un banner alla prima visita, salva la scelta
// dell'utente e pilota Google Consent Mode v2 (analytics_storage).
//
// Categorie:
//   - "necessari": sempre attivi (nessun cookie di tracciamento).
//   - "analytics": Google Analytics. Bloccato finché l'utente non acconsente.
//
// Approccio OPT-IN (consenso preventivo): è il più rigoroso e va bene a livello
// globale. Vedi privacy.html per l'informativa.

(function () {
  'use strict';

  var KEY = 'bitgen_consent_v1';
  var POLICY_URL = 'privacy.html';

  function getConsent() {
    try { return JSON.parse(localStorage.getItem(KEY)); } catch (e) { return null; }
  }
  function setConsent(c) {
    c.ts = new Date().toISOString();
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {}
  }

  // Comunica la scelta a Google Consent Mode (gtag è definito nell'inline in <head>)
  function applyConsent(c) {
    if (typeof window.gtag === 'function') {
      window.gtag('consent', 'update', {
        analytics_storage: c && c.analytics ? 'granted' : 'denied'
        // ad_storage / ad_* restano "denied": il sito non fa pubblicità.
      });
    }
  }

  // Applica subito la scelta già salvata (così al ritorno l'utente non rivede il banner)
  var saved = getConsent();
  if (saved) applyConsent(saved);

  // ---------- UI ----------
  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  var overlay = null;

  function close() {
    if (overlay) { overlay.remove(); overlay = null; }
  }

  function decide(analytics) {
    var c = { necessary: true, analytics: !!analytics };
    setConsent(c);
    applyConsent(c);
    close();
  }

  function showBanner(forcePrefs) {
    close();
    overlay = el('div', 'cc-overlay');

    var card = el('div', 'cc-card');
    card.setAttribute('role', 'dialog');
    card.setAttribute('aria-label', 'Informativa cookie');

    card.appendChild(el('h3', 'cc-title', '🍪 Rispettiamo la tua privacy'));
    card.appendChild(el('p', 'cc-text',
      'Usiamo cookie tecnici (sempre attivi) e, solo con il tuo consenso, ' +
      'Google Analytics per capire come viene usato il sito. Puoi accettare, ' +
      'rifiutare o scegliere. Trovi i dettagli nella ' +
      '<a href="' + POLICY_URL + '">Cookie Policy</a>.'));

    // Pannello preferenze (Analytics)
    var prefs = el('div', 'cc-prefs');
    var rowNec = el('div', 'cc-row',
      '<div><strong>Necessari</strong><br><span class="cc-muted">Indispensabili al funzionamento del sito.</span></div>' +
      '<span class="cc-always">Sempre attivi</span>');
    var rowAna = el('label', 'cc-row');
    rowAna.innerHTML =
      '<div><strong>Analitici (Google Analytics)</strong><br><span class="cc-muted">Statistiche anonime di utilizzo.</span></div>';
    var toggle = el('input');
    toggle.type = 'checkbox';
    toggle.className = 'cc-toggle';
    toggle.checked = saved ? !!saved.analytics : false;
    rowAna.appendChild(toggle);
    prefs.appendChild(rowNec);
    prefs.appendChild(rowAna);
    if (!forcePrefs) prefs.style.display = 'none';

    // Azioni
    var actions = el('div', 'cc-actions');
    var btnPrefs = el('button', 'cc-btn cc-btn-ghost', 'Personalizza');
    btnPrefs.type = 'button';
    var btnSave = el('button', 'cc-btn cc-btn-ghost', 'Salva preferenze');
    btnSave.type = 'button';
    btnSave.style.display = forcePrefs ? '' : 'none';
    var btnReject = el('button', 'cc-btn cc-btn-secondary', 'Rifiuta');
    btnReject.type = 'button';
    var btnAccept = el('button', 'cc-btn cc-btn-primary', 'Accetta');
    btnAccept.type = 'button';

    btnPrefs.addEventListener('click', function () {
      var open = prefs.style.display !== 'none';
      prefs.style.display = open ? 'none' : 'block';
      btnSave.style.display = open ? 'none' : '';
    });
    btnSave.addEventListener('click', function () { decide(toggle.checked); });
    btnReject.addEventListener('click', function () { decide(false); });
    btnAccept.addEventListener('click', function () { decide(true); });

    actions.appendChild(btnPrefs);
    actions.appendChild(btnSave);
    actions.appendChild(btnReject);
    actions.appendChild(btnAccept);

    card.appendChild(prefs);
    card.appendChild(actions);
    overlay.appendChild(card);
    document.body.appendChild(overlay);
  }

  // Link "Preferenze cookie" nel footer (per riaprire e cambiare idea)
  function addFooterLink() {
    var bottoms = document.querySelectorAll('.footer-bottom');
    bottoms.forEach(function (fb) {
      if (fb.querySelector('.cc-reopen')) return;
      var wrap = el('div');
      var a = el('a', 'cc-reopen', '🍪 Preferenze cookie');
      a.href = '#';
      a.addEventListener('click', function (ev) { ev.preventDefault(); showBanner(true); });
      var sep = document.createTextNode(' · ');
      var priv = el('a', 'cc-reopen', 'Privacy & Cookie');
      priv.href = POLICY_URL;
      wrap.appendChild(a);
      wrap.appendChild(sep);
      wrap.appendChild(priv);
      fb.appendChild(wrap);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    addFooterLink();
    if (!getConsent()) showBanner(false);
  });

  // API pubblica per riaprire le preferenze da qualsiasi punto
  window.bitgenCookiePrefs = function () { showBanner(true); };
})();
