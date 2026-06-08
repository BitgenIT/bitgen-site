// ============================================
// BITGEN - CONFIGURAZIONE CENTRALE
// ============================================
// Questo è il file dove imposti TUTTO una volta sola.
// Dopo aver modificato questi valori, si applicano a tutte le pagine.

const BITGEN_CONFIG = {
  
  // ────────────────────────────────────────
  // INFORMAZIONI BASE DEL SITO
  // ────────────────────────────────────────
  site: {
    name: "BItGen",
    tagline: "Educazione Digitale per Tutti",
    description: "Il canale di divulgazione informatica che spiega davvero come funziona la tecnologia. Guide, tutorial e approfondimenti per chi vuole capire, non solo usare.",
    url: "https://bitgen.it", // ⚠️ Cambia con il tuo dominio reale
    author: "BItGen",
    language: "it",
    locale: "it_IT",
    email: "info@bitgen.it",
    logoUrl: "assets/images/logo.png",
    ogImageUrl: "assets/images/logo.png", // Immagine per anteprime social (1200x630 consigliato)
  },
  
  // ────────────────────────────────────────
  // GOOGLE ANALYTICS
  // ────────────────────────────────────────
  // Per attivare:
  // 1. Vai su https://analytics.google.com
  // 2. Crea una proprietà GA4 per il tuo sito
  // 3. Copia il Measurement ID (formato: G-XXXXXXXXXX)
  // 4. Incollalo qui sotto
  // 5. Il tracciamento si attiva automaticamente su tutte le pagine
  analytics: {
    enabled: false, // ⚠️ Cambia in true dopo aver inserito l'ID
    measurementId: "G-XXXXXXXXXX", // ⚠️ Sostituisci con il tuo ID reale
  },
  
  // ────────────────────────────────────────
  // NEWSLETTER
  // ────────────────────────────────────────
  // Scegli un provider tra: "mailchimp", "brevo", "substack", "disabled"
  // Per i dettagli di configurazione vedi README
  newsletter: {
    enabled: true,
    provider: "formspree", // "mailchimp" | "brevo" | "substack" | "formspree" | "disabled"
    
    // Per Formspree (il più semplice, consigliato per iniziare)
    // 1. Registrati su https://formspree.io (gratis fino a 50 submission/mese)
    // 2. Crea un nuovo form
    // 3. Copia l'endpoint URL qui sotto
    formspreeEndpoint: "https://formspree.io/f/xxxxxxxx", // ⚠️ Sostituisci
    
    // Per Mailchimp
    mailchimpFormUrl: "", // URL del form di iscrizione (se usi Mailchimp)
    
    // Per Brevo (ex Sendinblue)
    brevoListId: "", // ID lista Brevo
    brevoApiKey: "", // ⚠️ Da gestire lato backend per sicurezza
    
    // Per Substack
    substackUrl: "https://bitgen.substack.com", // Il tuo URL Substack
  },
  
  // ────────────────────────────────────────
  // SOCIAL LINKS
  // ────────────────────────────────────────
  social: {
    youtube: "https://youtube.com/@BItGen",
    instagram: "https://instagram.com/bitgen.channel",
    tiktok: "https://tiktok.com/@bitgen",
    linkedin: "https://linkedin.com/company/bitgen",
    twitter: "", // Opzionale
  },
  
  // ────────────────────────────────────────
  // PAROLE RISERVATE PER LA RICERCA
  // ────────────────────────────────────────
  // Parole da ignorare nella ricerca (articoli, preposizioni, ecc.)
  searchStopWords: [
    "il", "la", "lo", "i", "gli", "le", "un", "una", "uno",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "ed", "o", "ma", "che", "se", "come", "quando",
    "the", "a", "an", "of", "to", "in", "for", "on", "at", "is", "are"
  ],
  
  // ────────────────────────────────────────
  // IMPOSTAZIONI ENCICLOPEDIA
  // ────────────────────────────────────────
  enciclopedia: {
    articlesPerPage: 12, // Paginazione (se abiliti paginazione in futuro)
    defaultSort: "data-desc", // "data-desc" | "data-asc" | "titolo-asc"
    wordsPerMinute: 220, // Velocità di lettura italiana media per il calcolo del tempo
  },
  
};

// Esporta per uso nelle pagine
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BITGEN_CONFIG;
}
