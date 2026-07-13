// ============================================
// BITGEN - GUIDE (PERCORSI DI LETTURA)
// ============================================
//
// Una "guida" è un percorso ordinato di articoli GIÀ presenti in enciclopedia,
// pensato per imparare un argomento passo dopo passo. Il lettore può segnare
// gli articoli che ha già letto: il progresso viene salvato nel browser
// (localStorage), senza account.
//
// ⚠️ FORMATO DATI: questo blocco è scritto e riletto dai tool Python in JSON,
// esattamente come data.js. Modifica le guide con il tool "gestisci_guide.py"
// (o dal menu di aggiungi_articolo.py): è più sicuro che editare a mano.
// Se editi a mano, mantieni un JSON valido (virgolette doppie, niente virgola
// finale dopo l'ultimo elemento).
//
// Campi di una guida:
//   - titolo        (obbligatorio) — diventa anche lo slug/id nell'URL (?g=slug)
//   - descrizione   (una frase che spiega a chi serve la guida)
//   - icona         (una emoji mostrata sulla card)
//   - livello       ("Base" | "Intermedio" | "Avanzato")
//   - articoli      (lista ORDINATA di id/slug di articoli esistenti in data.js)
//   - id            (opzionale: se assente viene calcolato dallo slug del titolo)
// ============================================

function slugifyGuida(text) {
  text = (text || "").toLowerCase();
  text = text.normalize('NFD').replace(/[̀-ͯ]/g, '');
  text = text.replace(/[^a-z0-9\s-]/g, '');
  text = text.replace(/\s+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
  return text.slice(0, 60);
}

const guideGrezze = [
  {
    "titolo": "Usare il computer dalle basi",
    "descrizione": "Parti da zero: cosa c'è dentro un PC, come sono fatti i file, come gestirli senza fare danni.",
    "icona": "🖥️",
    "livello": "Base",
    "articoli": [
      "cpu-ram-disco-spiegati-con-una-cucina",
      "bit-e-byte-perche-i-tuoi-file-pesano-in-kb-mb-e-gb",
      "come-strutturato-un-file-dentro-ce-piu-di-quello-che-vedi",
      "i-file-nascosti-di-windows-cosa-sono-e-come-mostrarli-senza-",
      "fat32-exfat-ntfs-e-gli-altri-cose-un-file-system-e-quale-sce",
      "cancellare-un-file-o-svuotare-il-cestino-lo-elimina-per-semp",
      "recuperare-file-cancellati-per-sbaglio",
      "creare-piu-account-utente-su-windows-e-gestirli",
      "devi-davvero-spegnere-il-pc-ogni-sera-sospensione-ibernazion",
      "cercare-file-cartelle-e-programmi-su-windows-linux-e-mac"
    ]
  },
  {
    "titolo": "Difenditi online: sicurezza di base",
    "descrizione": "Le poche abitudini che fermano il 99% dei guai: password, doppia verifica, truffe e backup.",
    "icona": "🔒",
    "livello": "Base",
    "articoli": [
      "virus-e-antivirus-il-vero-antivirus-sei-tu",
      "una-password-robusta-in-1-minuto-la-frase-al-posto-della-par",
      "password-manager-smetti-di-ricordare-le-password-e-falle-ric",
      "autenticazione-a-due-fattori-la-seconda-serratura-che-salva-",
      "phishing-come-riconoscere-lemail-che-finge-di-essere-la-tua-",
      "lsms-del-finto-corriere-cose-lo-smishing-e-come-non-cascarci",
      "salve-sono-il-supporto-microsoft-la-truffa-del-finto-tecnico",
      "virus-rilevato-i-finti-pop-up-allarmanti-e-le-estensioni-can",
      "ransomware-quando-un-virus-prende-in-ostaggio-i-tuoi-file-e-",
      "il-backup-e-la-tua-assicurazione-la-copia-che-ti-salva-da-vi"
    ]
  },
  {
    "titolo": "Il Wi-Fi di casa che funziona davvero",
    "descrizione": "Dai numeri sulla scatola del router alle zone morte: capisci e sistemi la tua rete senza fuffa.",
    "icona": "📶",
    "livello": "Base",
    "articoli": [
      "cose-il-wi-fi-no-non-e-internet",
      "wi-fi-5-6-6e-7-quel-numero-sulla-scatola-del-router-conta-da",
      "24-ghz-o-5-ghz-le-due-corsie-del-tuo-wi-fi-e-quando-usarle",
      "canali-wi-fi-perche-il-vicino-ti-rallenta-la-rete-e-come-sca",
      "cambiare-la-password-del-wi-fi-la-serratura-di-casa-che-non-",
      "aggiornare-il-firmware-del-router-il-tagliando-dimenticato-d",
      "il-wi-fi-non-arriva-in-camera-ripetitore-mesh-o-powerline",
      "access-point-vs-router-quando-una-sola-scatola-non-basta-piu",
      "dove-mettere-laccess-point-la-guida-al-posizionamento-del-wi",
      "rete-mesh-si-o-no-quando-conviene-davvero-e-quando-e-uno-spr"
    ]
  },
  {
    "titolo": "Capire le reti di computer",
    "descrizione": "Dal 'cos'è una rete' a IP, DNS e pacchetti: le fondamenta per capire come parlano i dispositivi.",
    "icona": "🌐",
    "livello": "Intermedio",
    "articoli": [
      "reti-per-umani-cose-davvero-una-rete-e-perche-lan-non-e-wan",
      "cose-il-wi-fi-no-non-e-internet",
      "indirizzo-ip-il-numero-civico-del-tuo-dispositivo-e-perche-n",
      "dns-la-rubrica-telefonica-che-traduce-i-nomi-dei-siti-in-num",
      "indirizzo-mac-limpronta-digitale-stampata-nella-tua-scheda-d",
      "hub-switch-e-router-chi-fa-cosa-nella-scatola-dei-cavi",
      "le-porte-di-comunicazione-65535-finestre-sul-tuo-dispositivo",
      "i-7-livelli-del-modello-isoosi-il-viaggio-di-un-pacchetto-pi",
      "topologie-di-rete-stella-albero-anello-bus-e-maglia-quale-qu"
    ]
  },
  {
    "titolo": "Comprare o aggiornare un PC",
    "descrizione": "CPU, RAM, disco, scheda video e alimentatore: cosa conta davvero prima di spendere (o aggiornare).",
    "icona": "🧩",
    "livello": "Intermedio",
    "articoli": [
      "cpu-ram-disco-spiegati-con-una-cucina",
      "come-funziona-un-processore-dentro-la-cpu-e-il-ciclo-che-ese",
      "cose-il-socket-della-cpu-e-perche-determina-cosa-puoi-montar",
      "ddr-dimm-e-so-dimm-capire-i-moduli-di-ram-e-le-generazioni-d",
      "piu-ram-pc-piu-veloce-non-sempre",
      "ssd-vs-hdd-perche-il-tuo-vecchio-pc-sembra-rinascere",
      "scheda-video-gpu-il-chip-dei-videogiochi-che-oggi-muove-anch",
      "come-scegliere-lalimentatore-del-pc-psu-watt-efficienza-e-co",
      "aggiungere-o-sostituire-ram-e-ssd-lupgrade-che-ringiovanisce",
      "come-cambiare-la-scheda-grafica-gpu-passo-passo"
    ]
  },
  {
    "titolo": "Stampanti: installarle e non impazzire",
    "descrizione": "Installazione, driver, condivisione in rete e scansioni: la stampante domata una volta per tutte.",
    "icona": "🖨️",
    "livello": "Base",
    "articoli": [
      "installare-una-stampante-via-ip-o-con-il-programma-del-produ",
      "manca-un-driver-come-scoprirlo-e-risolvere-con-gestione-disp",
      "condividere-una-cartella-in-rete-e-decidere-chi-puo-accedere",
      "convertire-un-file-da-word-a-pdf-e-ritorno-senza-siti-loschi",
      "scansionare-un-documento-col-telefono-addio-scanner-ingombra"
    ]
  }
];

// Normalizza: calcola id/slug e garantisce che 'articoli' sia sempre una lista.
const guide = guideGrezze
  .map(function (g) {
    var n = Object.assign({}, g);
    if (!n.id) n.id = slugifyGuida(n.titolo || '');
    if (!Array.isArray(n.articoli)) n.articoli = [];
    return n;
  })
  .filter(function (g) { return g.titolo; });

// Esporta per uso nei tool / test (in browser resta globale)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { guide: guide, guideGrezze: guideGrezze };
}
