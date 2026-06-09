// ============================================
// BITGEN - GOOGLE CONSENT MODE V2
// ============================================
// CARICAMENTO: questo file va PRIMA di Cookiebot e PRIMA di config.js
//
// Ordine corretto nei file HTML:
//   1. consent-defaults.js  ← QUESTO FILE
//   2. Script Cookiebot     ← lo snippet che hai da Cookiebot
//   3. config.js
//   4. data.js
//   5. main.js
// ============================================

// Inizializza dataLayer (Google Tag Manager / Analytics)
window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}

// ─── CONSENT MODE V2: STATI PREDEFINITI ───
// Tutto NEGATO di default per utenti EU (GDPR)
// Analytics e marketing si attivano SOLO dopo il consenso esplicito
gtag('consent', 'default', {
  'analytics_storage': 'denied',
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'functionality_storage': 'denied',
  'personalization_storage': 'denied',
  'security_storage': 'granted',
  'wait_for_update': 500
});

// ─── LISTENER COOKIEBOT ───
// Quando l'utente clicca nel banner, aggiorna lo stato di consenso Google
window.addEventListener('CookiebotOnAccept', function() {
  if (typeof Cookiebot !== 'undefined') {
    gtag('consent', 'update', {
      'analytics_storage': Cookiebot.consent.statistics ? 'granted' : 'denied',
      'ad_storage': Cookiebot.consent.marketing ? 'granted' : 'denied',
      'ad_user_data': Cookiebot.consent.marketing ? 'granted' : 'denied',
      'ad_personalization': Cookiebot.consent.marketing ? 'granted' : 'denied',
      'functionality_storage': Cookiebot.consent.preferences ? 'granted' : 'denied',
      'personalization_storage': Cookiebot.consent.preferences ? 'granted' : 'denied',
    });
  }
});

// Anche quando l'utente rifiuta
window.addEventListener('CookiebotOnDecline', function() {
  gtag('consent', 'update', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
  });
});
