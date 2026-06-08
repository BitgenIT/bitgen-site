// ============================================
// BITGEN - MAIN JAVASCRIPT
// Ricerca, filtri, SEO dinamico, Analytics, Newsletter
// ============================================

// ============================================
// GOOGLE ANALYTICS - Inizializzazione automatica
// ============================================

function initAnalytics() {
  if (!BITGEN_CONFIG.analytics.enabled || !BITGEN_CONFIG.analytics.measurementId) return;
  if (BITGEN_CONFIG.analytics.measurementId === "G-XXXXXXXXXX") return;
  
  const id = BITGEN_CONFIG.analytics.measurementId;
  
  // Carica gtag.js
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${id}`;
  document.head.appendChild(script);
  
  // Inizializza dataLayer
  window.dataLayer = window.dataLayer || [];
  window.gtag = function() { dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', id, {
    'anonymize_ip': true, // GDPR-friendly
    'cookie_flags': 'SameSite=None;Secure'
  });
}

/** Traccia un evento custom (es. lettura articolo, click su newsletter) */
function trackEvent(eventName, params = {}) {
  if (typeof window.gtag === 'function') {
    window.gtag('event', eventName, params);
  }
}


// ============================================
// SEO DINAMICO - Gestione meta tag per pagina
// ============================================

/** Imposta i meta tag SEO per la pagina corrente */
function setSEO({ title, description, image, url, type = 'website', keywords = [], publishedDate = null, modifiedDate = null }) {
  const cfg = BITGEN_CONFIG.site;
  const fullTitle = title ? `${title} — ${cfg.name}` : `${cfg.name} — ${cfg.tagline}`;
  const finalDesc = description || cfg.description;
  const finalImage = image || cfg.ogImageUrl;
  const finalUrl = url || window.location.href;
  
  // Imposta title
  document.title = fullTitle;
  
  // Helper: aggiorna o crea meta tag
  const setMeta = (name, content, isProperty = false) => {
    const attr = isProperty ? 'property' : 'name';
    let tag = document.querySelector(`meta[${attr}="${name}"]`);
    if (!tag) {
      tag = document.createElement('meta');
      tag.setAttribute(attr, name);
      document.head.appendChild(tag);
    }
    tag.setAttribute('content', content);
  };
  
  // Standard meta
  setMeta('description', finalDesc);
  if (keywords.length > 0) setMeta('keywords', keywords.join(', '));
  setMeta('author', cfg.author);
  
  // Open Graph (Facebook, WhatsApp, LinkedIn)
  setMeta('og:title', fullTitle, true);
  setMeta('og:description', finalDesc, true);
  setMeta('og:image', new URL(finalImage, window.location.href).href, true);
  setMeta('og:url', finalUrl, true);
  setMeta('og:type', type, true);
  setMeta('og:site_name', cfg.name, true);
  setMeta('og:locale', cfg.locale, true);
  
  // Twitter Card
  setMeta('twitter:card', 'summary_large_image');
  setMeta('twitter:title', fullTitle);
  setMeta('twitter:description', finalDesc);
  setMeta('twitter:image', new URL(finalImage, window.location.href).href);
  
  // Canonical URL
  let canonical = document.querySelector('link[rel="canonical"]');
  if (!canonical) {
    canonical = document.createElement('link');
    canonical.rel = 'canonical';
    document.head.appendChild(canonical);
  }
  canonical.href = finalUrl;
  
  // Article-specific
  if (type === 'article') {
    if (publishedDate) setMeta('article:published_time', publishedDate, true);
    if (modifiedDate) setMeta('article:modified_time', modifiedDate, true);
    setMeta('article:author', cfg.author, true);
  }
}

/** Aggiunge Schema.org structured data per SEO avanzato */
function addStructuredData(data) {
  // Rimuovi precedente se esiste
  const existing = document.querySelector('script[type="application/ld+json"]#bitgen-schema');
  if (existing) existing.remove();
  
  const script = document.createElement('script');
  script.type = 'application/ld+json';
  script.id = 'bitgen-schema';
  script.textContent = JSON.stringify(data);
  document.head.appendChild(script);
}


// ============================================
// UTILITY FUNCTIONS
// ============================================

function formatDate(isoDate) {
  const date = new Date(isoDate);
  const months = ['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
                  'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'];
  return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
}

function getRubricaColor(rubrica) {
  const colors = {
    "Ma cos'è?": "#10b981",
    "Sotto il Cofano": "#3b82f6",
    "Digitale Pratico": "#f59e0b",
    "Miti Digitali": "#a855f7",
    "Il Dietro le Quinte": "#ec4899"
  };
  return colors[rubrica] || "#22c55e";
}

function getRubricaIcon(rubrica) {
  const icons = {
    "Ma cos'è?": "💡",
    "Sotto il Cofano": "🔧",
    "Digitale Pratico": "🎯",
    "Miti Digitali": "⚡",
    "Il Dietro le Quinte": "🧠"
  };
  return icons[rubrica] || "📝";
}

function getReadingTime(content) {
  const wpm = BITGEN_CONFIG.enciclopedia.wordsPerMinute || 220;
  const words = content.split(/\s+/).length;
  const minutes = Math.max(1, Math.ceil(words / wpm));
  return `${minutes} min lettura`;
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}


// ============================================
// RICERCA
// ============================================

function searchArticoli(query) {
  if (!query || query.trim().length < 2) return [];
  
  const stopWords = new Set(BITGEN_CONFIG.searchStopWords || []);
  const q = query.toLowerCase().trim();
  const queryWords = q.split(/\s+/).filter(w => w.length > 1 && !stopWords.has(w));
  
  if (queryWords.length === 0) return [];
  
  return articoli.filter(art => {
    const searchableText = [
      art.titolo, art.estratto, art.contenuto, art.rubrica,
      (art.tags || []).join(' ')
    ].join(' ').toLowerCase();
    return queryWords.every(word => searchableText.includes(word));
  }).map(art => {
    let score = 0;
    const title = art.titolo.toLowerCase();
    const excerpt = art.estratto.toLowerCase();
    queryWords.forEach(word => {
      if (title.includes(word)) score += 10;
      if (excerpt.includes(word)) score += 5;
      if (art.tags && art.tags.some(t => t.toLowerCase().includes(word))) score += 3;
    });
    return { ...art, _score: score };
  }).sort((a, b) => b._score - a._score);
}

function initHeaderSearch() {
  const searchInputs = document.querySelectorAll('.search-input');
  const searchResultsContainers = document.querySelectorAll('.search-results');
  
  searchInputs.forEach((input, index) => {
    const resultsContainer = searchResultsContainers[index];
    if (!resultsContainer) return;
    
    let debounceTimer;
    
    input.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value;
      if (query.length < 2) {
        resultsContainer.classList.remove('active');
        return;
      }
      debounceTimer = setTimeout(() => {
        const results = searchArticoli(query);
        renderSearchResults(resultsContainer, results, query);
        if (results.length > 0) trackEvent('search', { search_term: query });
      }, 200);
    });
    
    input.addEventListener('focus', (e) => {
      if (e.target.value.length >= 2) {
        const results = searchArticoli(e.target.value);
        renderSearchResults(resultsContainer, results, e.target.value);
      }
    });
    
    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !resultsContainer.contains(e.target)) {
        resultsContainer.classList.remove('active');
      }
    });
    
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        const query = e.target.value.trim();
        if (query) {
          window.location.href = `enciclopedia.html?q=${encodeURIComponent(query)}`;
        }
      }
    });
  });
}

function renderSearchResults(container, results, query) {
  if (results.length === 0) {
    container.innerHTML = `
      <div class="search-empty">
        Nessun risultato per "<strong>${escapeHtml(query)}</strong>"
      </div>
    `;
    container.classList.add('active');
    return;
  }
  
  const displayedResults = results.slice(0, 6);
  container.innerHTML = displayedResults.map(art => `
    <a href="articolo.html?id=${art.id}" class="search-result-item">
      <div class="search-result-rubrica">${getRubricaIcon(art.rubrica)} ${art.rubrica}</div>
      <div class="search-result-title">${escapeHtml(art.titolo)}</div>
      <div class="search-result-excerpt">${escapeHtml(art.estratto)}</div>
    </a>
  `).join('') + (results.length > 6 ? `
    <a href="enciclopedia.html?q=${encodeURIComponent(query)}" class="search-result-item" style="text-align:center;font-weight:600;color:var(--green-darker);">
      Vedi tutti i ${results.length} risultati →
    </a>
  ` : '');
  container.classList.add('active');
}


// ============================================
// RENDERING ARTICOLI
// ============================================

function createArticleCard(art, featured = false) {
  const color = getRubricaColor(art.rubrica);
  const icon = getRubricaIcon(art.rubrica);
  
  return `
    <a href="articolo.html?id=${art.id}" class="article-card">
      <div class="article-thumbnail" style="background: linear-gradient(135deg, ${color}dd 0%, ${color} 100%);">
        <div class="article-rubrica-badge">${icon} ${art.rubrica}</div>
        <div class="article-duration">▶ ${art.durata}</div>
        <div class="article-thumbnail-inner">BItGen</div>
      </div>
      <div class="article-content">
        <div class="article-meta">
          <span>${formatDate(art.data)}</span>
          <span>•</span>
          <span>${getReadingTime(art.contenuto)}</span>
        </div>
        <h3>${escapeHtml(art.titolo)}</h3>
        <p class="article-excerpt">${escapeHtml(art.estratto)}</p>
        <div class="article-footer">
          <div class="article-tags">
            ${(art.tags || []).slice(0, 2).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
          </div>
          <span class="article-arrow">Leggi →</span>
        </div>
      </div>
    </a>
  `;
}

function renderLatestArticles() {
  const container = document.getElementById('latest-articles');
  if (!container) return;
  
  const sorted = [...articoli].sort((a, b) => new Date(b.data) - new Date(a.data));
  const latest = sorted.slice(0, 5);
  container.innerHTML = latest.map((art, idx) => createArticleCard(art, idx === 0)).join('');
}


// ============================================
// ENCICLOPEDIA PAGE
// ============================================

let currentFilter = 'all';
let currentSearchQuery = '';

function renderEnciclopedia() {
  const container = document.getElementById('enciclopedia-grid');
  const countEl = document.getElementById('filter-count');
  if (!container) return;
  
  let filtered = [...articoli];
  
  if (currentFilter !== 'all') {
    filtered = filtered.filter(a => a.rubrica === currentFilter);
  }
  
  if (currentSearchQuery) {
    filtered = searchArticoli(currentSearchQuery).filter(a => 
      currentFilter === 'all' || a.rubrica === currentFilter
    );
  } else {
    filtered.sort((a, b) => new Date(b.data) - new Date(a.data));
  }
  
  if (countEl) {
    countEl.innerHTML = `<strong>${filtered.length}</strong> ${filtered.length === 1 ? 'risultato' : 'risultati'}`;
  }
  
  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="no-results" style="grid-column: 1/-1;">
        <div class="no-results-icon">🔍</div>
        <h3>Nessun risultato trovato</h3>
        <p>Prova a modificare i filtri o a cercare qualcos'altro.</p>
        <button class="btn btn-secondary" onclick="resetFilters()">Reset filtri</button>
      </div>
    `;
  } else {
    container.innerHTML = filtered.map(art => createArticleCard(art)).join('');
  }
}

function resetFilters() {
  currentFilter = 'all';
  currentSearchQuery = '';
  const searchInput = document.getElementById('enciclopedia-search');
  if (searchInput) searchInput.value = '';
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.filter === 'all');
  });
  renderEnciclopedia();
}

function initEnciclopedia() {
  const filterButtons = document.querySelectorAll('.filter-btn');
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter;
      renderEnciclopedia();
      trackEvent('filter_rubrica', { rubrica: currentFilter });
    });
  });
  
  const searchInput = document.getElementById('enciclopedia-search');
  if (searchInput) {
    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        currentSearchQuery = e.target.value.trim();
        renderEnciclopedia();
      }, 200);
    });
  }
  
  const urlParams = new URLSearchParams(window.location.search);
  const queryParam = urlParams.get('q');
  if (queryParam && searchInput) {
    searchInput.value = queryParam;
    currentSearchQuery = queryParam;
  }
  
  // SEO per pagina enciclopedia
  setSEO({
    title: 'Enciclopedia',
    description: 'Tutti i contenuti di BItGen organizzati per rubrica. Cerca tra tutorial, approfondimenti, spiegazioni informatiche e smentite di miti digitali.',
    type: 'website',
    keywords: ['informatica', 'educazione digitale', 'tutorial pc', 'divulgazione tecnologica', 'italia']
  });
  
  renderEnciclopedia();
}


// ============================================
// ARTICOLO PAGE
// ============================================

function renderArticolo() {
  const container = document.getElementById('articolo-container');
  const relatedContainer = document.getElementById('related-articles');
  if (!container) return;
  
  const urlParams = new URLSearchParams(window.location.search);
  const id = urlParams.get('id');
  const art = articoli.find(a => a.id === id);
  
  if (!art) {
    setSEO({ title: 'Articolo non trovato', description: 'L\'articolo che cerchi non esiste o è stato rimosso.' });
    container.innerHTML = `
      <div class="no-results">
        <div class="no-results-icon">😕</div>
        <h3>Articolo non trovato</h3>
        <p>L'articolo che cerchi non esiste o è stato rimosso.</p>
        <a href="enciclopedia.html" class="btn btn-primary">Torna all'enciclopedia</a>
      </div>
    `;
    return;
  }
  
  // ═══════════════════════════════════════
  // SEO DINAMICO PER ARTICOLO
  // ═══════════════════════════════════════
  setSEO({
    title: art.titolo,
    description: art.estratto,
    type: 'article',
    keywords: [...(art.tags || []), art.rubrica, 'informatica', 'BItGen'],
    publishedDate: art.data,
    modifiedDate: art.data
  });
  
  // Structured Data (Schema.org Article)
  addStructuredData({
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": art.titolo,
    "description": art.estratto,
    "image": new URL(BITGEN_CONFIG.site.ogImageUrl, window.location.href).href,
    "author": {
      "@type": "Organization",
      "name": BITGEN_CONFIG.site.author,
      "url": BITGEN_CONFIG.site.url
    },
    "publisher": {
      "@type": "Organization",
      "name": BITGEN_CONFIG.site.name,
      "logo": {
        "@type": "ImageObject",
        "url": new URL(BITGEN_CONFIG.site.logoUrl, window.location.href).href
      }
    },
    "datePublished": art.data,
    "dateModified": art.data,
    "articleSection": art.rubrica,
    "keywords": (art.tags || []).join(', '),
    "inLanguage": BITGEN_CONFIG.site.language,
    "mainEntityOfPage": window.location.href
  });
  
  // Track view
  trackEvent('view_article', {
    article_id: art.id,
    article_title: art.titolo,
    article_rubrica: art.rubrica
  });
  
  const color = getRubricaColor(art.rubrica);
  const icon = getRubricaIcon(art.rubrica);
  
  // Formatta contenuto
  const formattedContent = art.contenuto
    .split(/\n\s*\n/)
    .map(block => {
      const trimmed = block.trim();
      if (!trimmed) return '';
      const lines = trimmed.split('\n').map(l => l.trim()).filter(l => l);
      const result = [];
      let currentParagraph = [];
      
      const flushParagraph = () => {
        if (currentParagraph.length > 0) {
          result.push(`<p>${escapeHtml(currentParagraph.join(' '))}</p>`);
          currentParagraph = [];
        }
      };
      
      lines.forEach(line => {
        const isSubtitle = line.length < 80 
          && line === line.toUpperCase() 
          && /[A-Z]/.test(line)
          && !line.endsWith('.') && !line.endsWith('?') && !line.endsWith('!');
        if (isSubtitle) {
          flushParagraph();
          result.push(`<h3>${escapeHtml(line)}</h3>`);
        } else {
          currentParagraph.push(line);
        }
      });
      flushParagraph();
      return result.join('');
    })
    .join('');
  
  container.innerHTML = `
    <div class="article-breadcrumb">
      <a href="index.html">Home</a>
      <span class="separator">/</span>
      <a href="enciclopedia.html">Enciclopedia</a>
      <span class="separator">/</span>
      <span>${escapeHtml(art.rubrica)}</span>
    </div>
    
    <div class="article-header">
      <div class="article-header-meta">
        <span class="article-rubrica-badge" style="background: ${color}22; color: ${color}; position: static;">
          ${icon} ${art.rubrica}
        </span>
        <span style="color: var(--text-muted); font-size: 0.9rem;">${formatDate(art.data)}</span>
        <span style="color: var(--text-muted); font-size: 0.9rem;">•</span>
        <span style="color: var(--text-muted); font-size: 0.9rem;">${getReadingTime(art.contenuto)}</span>
      </div>
      <h1>${escapeHtml(art.titolo)}</h1>
      <p class="article-excerpt-large">${escapeHtml(art.estratto)}</p>
      <div class="article-tags">
        ${(art.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}
      </div>
    </div>
    
    ${art.videoUrl && !art.videoUrl.includes('placeholder') ? `
      <div class="video-embed-container">
        <h4>▶️ Guarda il video su YouTube</h4>
        <a href="${escapeHtml(art.videoUrl)}" target="_blank" rel="noopener" class="video-link-btn" onclick="trackEvent('click_video', {article_id: '${art.id}'})">
          Vai al video
          <span>↗</span>
        </a>
      </div>
    ` : `
      <div class="video-embed-container" style="background: linear-gradient(135deg, var(--green-darker) 0%, var(--green-primary) 100%);">
        <h4>📺 Video in arrivo</h4>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0;">
          Questo contenuto è parte del piano editoriale di BItGen. Il video sarà pubblicato prossimamente.
        </p>
      </div>
    `}
    
    <div class="article-body">
      ${formattedContent}
    </div>
    
    <div class="article-footer-share">
      <a href="enciclopedia.html" class="btn btn-secondary">← Torna all'enciclopedia</a>
    </div>
  `;
  
  if (relatedContainer) {
    const related = articoli
      .filter(a => a.id !== art.id && (a.rubrica === art.rubrica || 
        (a.tags || []).some(t => (art.tags || []).includes(t))))
      .slice(0, 3);
    
    if (related.length > 0) {
      relatedContainer.innerHTML = `
        <div class="container">
          <div class="section-header">
            <div class="section-title-group">
              <div class="section-eyebrow">Continua a leggere</div>
              <h2>Articoli correlati</h2>
            </div>
          </div>
          <div class="articoli-grid">
            ${related.map(a => createArticleCard(a)).join('')}
          </div>
        </div>
      `;
    }
  }
}


// ============================================
// MOBILE MENU
// ============================================

function initMobileMenu() {
  const toggle = document.querySelector('.mobile-toggle');
  const nav = document.querySelector('.nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('mobile-open');
    });
  }
}


// ============================================
// CONTACT FORM
// ============================================

function initContactForm() {
  const form = document.getElementById('contact-form');
  if (!form) return;
  
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const name = formData.get('name') || '';
    const email = formData.get('email') || '';
    const subject = formData.get('subject') || 'Contatto da BItGen';
    const message = formData.get('message') || '';
    
    const mailtoBody = `Nome: ${name}\nEmail: ${email}\n\nMessaggio:\n${message}`;
    const mailtoUrl = `mailto:${BITGEN_CONFIG.site.email}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(mailtoBody)}`;
    window.location.href = mailtoUrl;
    
    trackEvent('contact_submit', { subject });
    
    const submitBtn = form.querySelector('.form-submit');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = '✓ Apertura client email...';
    submitBtn.style.background = 'var(--green-darker)';
    setTimeout(() => {
      submitBtn.textContent = originalText;
      submitBtn.style.background = '';
    }, 3000);
  });
}


// ============================================
// NEWSLETTER FORM
// ============================================

function initNewsletterForm() {
  const forms = document.querySelectorAll('.newsletter-form');
  if (forms.length === 0) return;
  
  const provider = BITGEN_CONFIG.newsletter.provider;
  
  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = form.querySelector('input[type="email"]');
      const btn = form.querySelector('button[type="submit"]');
      const feedback = form.querySelector('.newsletter-feedback') || createFeedbackEl(form);
      
      const email = input.value.trim();
      if (!email || !email.includes('@')) {
        feedback.textContent = 'Inserisci un\'email valida';
        feedback.className = 'newsletter-feedback error';
        return;
      }
      
      const originalText = btn.textContent;
      btn.disabled = true;
      btn.textContent = 'Iscrizione in corso…';
      
      try {
        if (provider === 'formspree') {
          await submitToFormspree(email);
        } else if (provider === 'substack') {
          window.open(BITGEN_CONFIG.newsletter.substackUrl, '_blank');
          feedback.textContent = '✓ Apertura Substack per completare l\'iscrizione';
          feedback.className = 'newsletter-feedback success';
          btn.textContent = originalText;
          btn.disabled = false;
          return;
        } else if (provider === 'mailchimp') {
          // Mailchimp richiede redirect al form action
          form.submit();
          return;
        } else {
          throw new Error('Provider newsletter non configurato');
        }
        
        feedback.textContent = '✓ Grazie! Controlla la tua email per confermare l\'iscrizione.';
        feedback.className = 'newsletter-feedback success';
        input.value = '';
        trackEvent('newsletter_subscribe', { method: provider });
      } catch (err) {
        feedback.textContent = 'Errore durante l\'iscrizione. Riprova tra poco.';
        feedback.className = 'newsletter-feedback error';
        console.error(err);
      } finally {
        btn.disabled = false;
        btn.textContent = originalText;
      }
    });
  });
}

function createFeedbackEl(form) {
  const el = document.createElement('div');
  el.className = 'newsletter-feedback';
  form.appendChild(el);
  return el;
}

async function submitToFormspree(email) {
  const endpoint = BITGEN_CONFIG.newsletter.formspreeEndpoint;
  if (!endpoint || endpoint.includes('xxxxxxxx')) {
    throw new Error('Formspree endpoint non configurato');
  }
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: JSON.stringify({ email, _subject: 'Nuova iscrizione BItGen newsletter' })
  });
  if (!response.ok) throw new Error('Formspree error');
  return response.json();
}


// ============================================
// PAGE-SPECIFIC SEO
// ============================================

function setSEOForPage(page) {
  switch (page) {
    case 'home':
      setSEO({
        title: null, // usa il default del sito
        description: BITGEN_CONFIG.site.description,
        type: 'website',
        keywords: ['informatica', 'educazione digitale', 'tutorial tecnologia', 'BItGen', 'divulgazione informatica', 'italia']
      });
      // Structured Data: WebSite + Organization
      addStructuredData({
        "@context": "https://schema.org",
        "@graph": [
          {
            "@type": "WebSite",
            "@id": `${BITGEN_CONFIG.site.url}/#website`,
            "url": BITGEN_CONFIG.site.url,
            "name": BITGEN_CONFIG.site.name,
            "description": BITGEN_CONFIG.site.tagline,
            "inLanguage": BITGEN_CONFIG.site.language,
            "potentialAction": {
              "@type": "SearchAction",
              "target": `${BITGEN_CONFIG.site.url}/enciclopedia.html?q={search_term_string}`,
              "query-input": "required name=search_term_string"
            }
          },
          {
            "@type": "Organization",
            "@id": `${BITGEN_CONFIG.site.url}/#organization`,
            "name": BITGEN_CONFIG.site.name,
            "url": BITGEN_CONFIG.site.url,
            "logo": new URL(BITGEN_CONFIG.site.logoUrl, BITGEN_CONFIG.site.url).href,
            "sameAs": Object.values(BITGEN_CONFIG.social).filter(v => v)
          }
        ]
      });
      break;
    
    case 'contatti':
      setSEO({
        title: 'Contatti',
        description: `Contatta ${BITGEN_CONFIG.site.name} per domande, collaborazioni, suggerimenti o segnalazioni.`,
        type: 'website',
        keywords: ['contatti', 'BItGen', 'informatica', 'divulgazione']
      });
      break;
  }
}


// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  initAnalytics();
  initHeaderSearch();
  initMobileMenu();
  initNewsletterForm();
  
  const page = document.body.dataset.page;
  
  switch (page) {
    case 'home':
      renderLatestArticles();
      setSEOForPage('home');
      break;
    case 'enciclopedia':
      initEnciclopedia();
      break;
    case 'articolo':
      renderArticolo();
      break;
    case 'contatti':
      initContactForm();
      setSEOForPage('contatti');
      break;
  }
  
  // Track page view
  trackEvent('page_view', { page_title: document.title, page_path: window.location.pathname });
});
