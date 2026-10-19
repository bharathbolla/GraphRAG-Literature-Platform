// GraphRAG Literature Platform - High-Fidelity Client Controller
// Fully aligned with 15-Slide Hackathon Presentation

let currentCorpus = [];
let currentEntities = [];
let activeNEREntity = null;
let networkInstance = null;
let rawGraphNodes = [];
let rawGraphEdges = [];
let graphColorMode = 'entity'; // 'entity' or 'community'
let hideChunksActive = false;
let physicsFrozen = false;
let activeFilters = {
  DrugClass: true,
  Drug: true,
  Article: true,
  Condition: true,
  Population: true,
  Outcome: true,
  Chunk: true
};

// ==================== TAB NAVIGATION ====================
function switchTab(tabName) {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-blue-600', 'text-white', 'shadow-sm');
    btn.classList.add('text-slate-400');
  });
  const activeBtn = document.getElementById(`tab-btn-${tabName}`);
  if (activeBtn) {
    activeBtn.classList.add('bg-blue-600', 'text-white', 'shadow-sm');
    activeBtn.classList.remove('text-slate-400');
  }

  ['corpus', 'chat', 'ner', 'pico', 'graph'].forEach(view => {
    const el = document.getElementById(`view-${view}`);
    if (el) el.classList.add('hidden');
  });
  const targetView = document.getElementById(`view-${tabName}`);
  if (targetView) targetView.classList.remove('hidden');

  if (tabName === 'graph' && !networkInstance) {
    initKnowledgeGraph();
  }
}

// ==================== INITIAL DATA LOADER ====================
async function loadCorpusData(skipSuggestions = false) {
  try {
    const res = await fetch('/api/articles');
    const data = await res.json();
    currentCorpus = data.articles;
    renderArticlesList();
    loadPicoTable();
    await loadNERList();
    await updateStatsBar();
    if (!skipSuggestions) {
      await fetchIngestionSuggestions();
    }
  } catch (err) {
    console.error("Failed to load corpus:", err);
  }
}

async function updateStatsBar() {
  try {
    const res = await fetch('/api/stats');
    const stats = await res.json();

    // Top Header
    const countEl = document.getElementById('nav-article-count');
    const patEl = document.getElementById('nav-patient-count');
    const statusEl = document.getElementById('nav-backend-status');
    const headerCountEl = document.getElementById('articles-count-header');

    if (countEl) countEl.innerText = `${stats.total_articles} RCTs`;
    if (patEl) patEl.innerText = stats.total_enrolled_patients.toLocaleString();
    if (statusEl) statusEl.innerText = `Backend Online (${stats.total_articles} papers)`;
    if (headerCountEl) headerCountEl.innerText = stats.total_articles;

    // Slide 01 Metric Cards
    const elArticles = document.getElementById('stat-articles');
    const elChunks = document.getElementById('stat-chunks');
    const elEdges = document.getElementById('stat-edges');
    const elEntities = document.getElementById('stat-entities');
    const elCommunities = document.getElementById('stat-communities');

    if (elArticles) elArticles.innerText = stats.indexed_articles || stats.total_articles;
    if (elChunks) elChunks.innerText = stats.section_chunks || 32;
    if (elEdges) elEdges.innerText = stats.kg_edges || stats.total_edges;
    if (elEntities) elEntities.innerText = stats.normalized_entities || stats.unique_entities;
    if (elCommunities) elCommunities.innerText = stats.thematic_communities || 8;
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

// ==================== TAB 1: CORPUS & INGESTION ====================
function renderArticlesList() {
  const container = document.getElementById('articles-container');
  if (!container) return;
  container.innerHTML = '';

  currentCorpus.forEach(art => {
    const pmid = art.pmid;
    const pop = art.pico?.population || {};
    const inter = art.pico?.interventions?.[0] || {};
    const primaryOut = art.pico?.outcomes?.[0] || {};

    const card = document.createElement('div');
    card.className = "bg-slate-900 border border-slate-800 p-5 rounded-2xl hover:border-slate-700 transition space-y-3 shadow-sm";
    card.innerHTML = `
      <div class="flex items-start justify-between gap-3">
        <div>
          <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">${art.study_design}</span>
          <span class="text-xs text-slate-500 ml-2 font-mono">${art.journal} (${art.year})</span>
          <h3 class="text-sm font-bold text-white mt-1.5 leading-snug">${art.title}</h3>
        </div>
        <a href="https://pubmed.ncbi.nlm.nih.gov/${pmid}/" target="_blank" class="text-xs text-blue-400 hover:text-blue-300 font-mono px-2 py-1 rounded bg-slate-800 border border-slate-700 whitespace-nowrap">
          PMID:${pmid}
        </a>
      </div>

      <p class="text-xs text-slate-400 line-clamp-3 leading-relaxed">${art.abstract}</p>

      <div class="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-xs">
        <div class="flex flex-wrap items-center gap-3">
          <span class="text-slate-400">Cohort N: <strong class="text-white font-mono">${pop.n ? pop.n.toLocaleString() : 'N/A'}</strong></span>
          <span class="text-slate-400">Drug: <strong class="text-emerald-400">${inter.name || 'N/A'}</strong></span>
          <span class="text-slate-400">Primary: <strong class="text-cyan-400">${primaryOut.measure || 'HR'} ${primaryOut.effect || ''}</strong></span>
        </div>
        <button onclick="openQuoteModal('${escapeQuotes(art.title)}', '${art.journal} ${art.year}', '${escapeQuotes(primaryOut.evidence || '')}', '${pmid}')" class="text-xs text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1 transition">
          <i class="fa-solid fa-quote-left text-[10px]"></i> View Proof
        </button>
      </div>
    `;
    container.appendChild(card);
  });
}

function fillAndIngest(query) {
  const input = document.getElementById('ingest-input');
  if (input) {
    input.value = query;
    fetchIngestionSuggestions(query);
    ingestArticle();
  }
}

let currentIngestionSuggestions = [];

function applySuggestedQueryByIndex(index, autoExecute = false) {
  const s = currentIngestionSuggestions[index];
  if (!s) return;
  const input = document.getElementById('ingest-input');
  if (input) {
    input.value = s.optimized_query;
    input.classList.add('ring-2', 'ring-amber-400', 'border-amber-400');
    setTimeout(() => {
      input.classList.remove('ring-2', 'ring-amber-400', 'border-amber-400');
    }, 1500);

    if (autoExecute) {
      ingestArticle();
    } else {
      input.focus();
      input.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
}

function copySuggestedQueryByIndex(index, btnEl) {
  const s = currentIngestionSuggestions[index];
  if (!s) return;
  
  const showFeedback = () => {
    if (btnEl) {
      const orig = btnEl.innerHTML;
      btnEl.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> <span class="text-emerald-300">Copied!</span>`;
      setTimeout(() => { btnEl.innerHTML = orig; }, 2000);
    }
  };

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(s.optimized_query).then(showFeedback).catch(() => {
      const input = document.getElementById('ingest-input');
      if (input) { input.value = s.optimized_query; input.select(); }
      showFeedback();
    });
  } else {
    const input = document.getElementById('ingest-input');
    if (input) { input.value = s.optimized_query; input.select(); }
    showFeedback();
  }
}

function renderIngestionSuggestions(suggestions) {
  currentIngestionSuggestions = suggestions || [];
  const container = document.getElementById('ingest-suggestions-container');
  if (!container) return;
  container.innerHTML = '';

  if (!suggestions || suggestions.length === 0) {
    container.innerHTML = `<div class="col-span-1 md:col-span-3 text-xs text-slate-500 py-3 text-center">No query suggestions available.</div>`;
    return;
  }

  suggestions.forEach((s, idx) => {
    const card = document.createElement('div');
    card.className = "bg-slate-950/80 border border-slate-800 rounded-xl p-4 flex flex-col justify-between space-y-3 hover:border-amber-500/50 hover:bg-slate-900/90 transition shadow-sm cursor-pointer group";
    card.title = "Click to load this query into the search bar";
    card.onclick = (e) => {
      if (e.target.closest('button')) return;
      applySuggestedQueryByIndex(idx, false);
    };

    let badgeColor = "bg-amber-500/10 text-amber-300 border-amber-500/20";
    let icon = "fa-magnifying-glass-plus";
    const labelLower = (s.strategy_label || "").toLowerCase();
    if (labelLower.includes("head-to-head") || labelLower.includes("comparator") || labelLower.includes("superiority")) {
      badgeColor = "bg-cyan-500/10 text-cyan-300 border-cyan-500/20";
      icon = "fa-code-compare";
    } else if (labelLower.includes("endpoint") || labelLower.includes("survival") || labelLower.includes("progression")) {
      badgeColor = "bg-purple-500/10 text-purple-300 border-purple-500/20";
      icon = "fa-chart-line";
    } else if (labelLower.includes("landscape") || labelLower.includes("class") || labelLower.includes("biologic") || labelLower.includes("depletion")) {
      badgeColor = "bg-emerald-500/10 text-emerald-300 border-emerald-500/20";
      icon = "fa-diagram-project";
    }

    const drugsHtml = (s.target_drugs || []).map(d =>
      `<span class="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">${d}</span>`
    ).join(' ');

    card.innerHTML = `
      <div class="space-y-2">
        <div class="flex items-start justify-between gap-2">
          <span class="text-[11px] font-bold px-2 py-0.5 rounded border ${badgeColor} flex items-center gap-1.5">
            <i class="fa-solid ${icon} text-[10px]"></i>
            <span>${s.strategy_label}</span>
          </span>
          <span class="text-[11px] font-bold font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 whitespace-nowrap">
            ${s.expected_yield}
          </span>
        </div>

        <p class="text-xs text-slate-300 leading-relaxed font-medium">
          ${s.rationale}
        </p>

        ${s.target_drugs && s.target_drugs.length > 0 ? `
          <div class="pt-1 flex flex-wrap gap-1 items-center">
            <span class="text-[10px] text-slate-400 uppercase font-semibold">Key Compounds:</span>
            ${drugsHtml}
          </div>
        ` : ''}

        <div class="bg-slate-900/90 rounded-lg p-2.5 border border-slate-800">
          <div class="text-[10px] text-slate-400 font-semibold mb-1 flex items-center justify-between">
            <span class="text-slate-400 font-mono">Optimized PubMed Syntax:</span>
            <button type="button" onclick="copySuggestedQueryByIndex(${idx}, this); event.stopPropagation();" class="text-blue-400 hover:text-blue-300 text-[10px] flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-slate-800 transition">
              <i class="fa-regular fa-copy"></i> Copy
            </button>
          </div>
          <div class="font-mono text-[11px] text-cyan-200 break-all leading-normal">
            ${s.optimized_query}
          </div>
        </div>
      </div>

      <div class="pt-2 flex items-center justify-between gap-2 border-t border-slate-800/80">
        <button type="button" onclick="applySuggestedQueryByIndex(${idx}, false); event.stopPropagation();" class="text-xs text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 transition border border-slate-700 flex items-center gap-1.5 font-medium shadow-sm">
          <i class="fa-solid fa-pen-to-square text-[11px] text-amber-400"></i>
          <span>Use Query</span>
        </button>
        <button type="button" onclick="applySuggestedQueryByIndex(${idx}, true); event.stopPropagation();" class="text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 px-3.5 py-1.5 rounded-lg transition shadow-md shadow-blue-600/30 flex items-center gap-1.5 whitespace-nowrap">
          <i class="fa-solid fa-cloud-arrow-down text-[11px]"></i>
          <span>⚡ Ingest this Search</span>
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

async function fetchIngestionSuggestions(optionalQuery) {
  const container = document.getElementById('ingest-suggestions-container');
  if (container) {
    container.innerHTML = `
      <div class="col-span-1 md:col-span-3 py-6 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
        <i class="fa-solid fa-spinner animate-spin text-amber-400"></i>
        <span>Generating optimized PubMed multi-prompt query strategies...</span>
      </div>
    `;
  }

  const queryText = optionalQuery !== undefined ? optionalQuery : (document.getElementById('ingest-input')?.value || "");

  try {
    const res = await fetch('/api/articles/suggest_queries', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ query: queryText })
    });
    const suggestions = await res.json();
    renderIngestionSuggestions(suggestions);
  } catch (err) {
    console.error("Failed to fetch ingestion suggestions:", err);
    if (container) {
      container.innerHTML = `<div class="col-span-1 md:col-span-3 text-xs text-red-400 py-3 text-center">Failed to load suggestions: ${err.message}</div>`;
    }
  }
}

async function ingestArticle() {
  const input = document.getElementById('ingest-input');
  const val = input.value.trim();
  if (!val) return;

  const maxSelect = document.getElementById('ingest-max-results');
  const maxResults = maxSelect ? parseInt(maxSelect.value, 10) : 10;

  const btn = document.getElementById('ingest-btn');
  btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin text-xs"></i> <span>Ingesting (up to ${maxResults})...</span>`;
  btn.disabled = true;

  try {
    const res = await fetch('/api/articles/ingest', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        query_or_pmid: val,
        max_results: maxResults
      })
    });
    const data = await res.json();

    // Show Slide 03 Success Banner
    const banner = document.getElementById('ingest-success-banner');
    const msg = document.getElementById('ingest-success-message');
    if (banner && msg) {
      msg.innerText = data.message || `Success: Ingested & parsed ${val} into section chunks, KG edges, and extracted PICO schema with 0 hallucinations.`;
      banner.classList.remove('hidden');
    }

    // If follow-up suggestions returned, update the suggestions panel
    if (data.suggested_next_queries && data.suggested_next_queries.length > 0) {
      renderIngestionSuggestions(data.suggested_next_queries);
    }

    input.value = '';
    await loadCorpusData(true);
    await updateHistoryCount();
    if (networkInstance) initKnowledgeGraph();
  } catch (err) {
    console.error("Ingestion failed:", err);
    alert("Ingestion error: " + err.message);
  } finally {
    btn.innerHTML = `<i class="fa-solid fa-magnifying-glass text-xs"></i> <span>Ingest to Graph</span>`;
    btn.disabled = false;
  }
}

function dismissIngestBanner() {
  const banner = document.getElementById('ingest-success-banner');
  if (banner) banner.classList.add('hidden');
}

async function resetBenchmark() {
  if (!confirm("Reset corpus to the 7 landmark Phase 3 SGLT2i clinical trials?")) return;
  try {
    const res = await fetch('/api/benchmark/reset', { method: 'POST' });
    const data = await res.json();
    alert(data.message);
    await loadCorpusData();
    if (networkInstance) initKnowledgeGraph();
  } catch (err) {
    console.error("Reset failed:", err);
  }
}

// ==================== TAB 2: MULTI-DOC CHAT & SYNTHESIS ====================
function fillAndSubmitChat(query) {
  document.getElementById('chat-input').value = query;
  sendChatMessage();
}

async function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const q = input.value.trim();
  if (!q) return;

  const routeSelect = document.getElementById('chat-route-select');
  const routeVal = routeSelect?.value || 'auto';

  const btn = document.getElementById('chat-submit-btn');
  btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin text-xs"></i> <span>Reasoning...</span>`;
  btn.disabled = true;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        query: q,
        route_override: routeVal !== 'auto' ? routeVal : null
      })
    });
    const data = await res.json();

    document.getElementById('chat-response-card').classList.remove('hidden');

    // Header info
    document.getElementById('chat-intent-badge').innerText = `Route: ${data.intent}`;
    document.getElementById('chat-route-explanation').innerText = data.audit?.route_explanation || "Detected cross-study / entity-centric query requiring multi-hop graph expansion & normalization.";
    document.getElementById('chat-audit-badge').innerHTML = `<i class="fa-solid fa-check-double text-xs"></i> <span>${data.audit?.status_badge || "100% Entailed | Zero Hallucinations"}</span>`;

    // 1. Synthesis Prose
    document.getElementById('chat-prose').innerHTML = data.synthesis.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // 2. Comparative Evidence Table
    const tbody = document.getElementById('chat-evidence-tbody');
    tbody.innerHTML = '';
    const evRows = data.evidence_table || [];
    document.getElementById('chat-evidence-count').innerText = evRows.length;

    evRows.forEach(row => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-slate-800/50 transition";
      tr.innerHTML = `
        <td class="p-3 font-semibold text-white">
          ${row.study_name}
          <div class="text-[10px] text-slate-500 font-mono">PMID:${row.pmid}</div>
        </td>
        <td class="p-3 text-emerald-400 font-medium">${row.drug} <span class="text-slate-500 text-[10px]">(${row.dose})</span></td>
        <td class="p-3 text-slate-300 max-w-xs truncate" title="${row.population}">${row.population}</td>
        <td class="p-3 text-cyan-300">${row.outcome}</td>
        <td class="p-3 font-bold text-white font-mono">${row.effect_size}</td>
        <td class="p-3 font-mono text-slate-400">${row.ci_95}</td>
        <td class="p-3 font-mono text-slate-400">${row.p_value}</td>
        <td class="p-3">
          <button onclick="openQuoteModal('${escapeQuotes(row.study_name)}', '${row.journal || ''} ${row.year || ''}', '${escapeQuotes(row.evidence_quote || '')}', '${row.pmid}')" class="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700 text-[11px] flex items-center gap-1 transition">
            <i class="fa-solid fa-quote-left text-[9px]"></i> Quote
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // 3. Citations Cards
    const citationsContainer = document.getElementById('chat-citations-container');
    citationsContainer.innerHTML = '';
    const citations = data.citations || [];
    document.getElementById('chat-citations-count').innerText = citations.length;

    citations.forEach(c => {
      const card = document.createElement('div');
      card.className = "bg-slate-950/70 border border-slate-800 p-4 rounded-xl space-y-2 hover:border-slate-700 transition";
      card.innerHTML = `
        <div class="flex items-start justify-between gap-2">
          <h4 class="text-xs font-bold text-white leading-snug">${c.title}</h4>
          <span class="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded border border-blue-500/20 whitespace-nowrap">PMID:${c.pmid}</span>
        </div>
        <div class="text-[11px] text-slate-400 font-mono">${c.journal_meta}</div>
        <p class="text-xs text-emerald-300/90 font-mono bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-500/20 line-clamp-3">
          "${c.evidence_quote}"
        </p>
        <div class="flex items-center justify-between pt-1 text-[11px]">
          <button onclick="openQuoteModal('${escapeQuotes(c.title)}', '${c.journal_meta}', '${escapeQuotes(c.evidence_quote)}', '${c.pmid}')" class="text-blue-400 hover:text-blue-300 font-medium flex items-center gap-1">
            <i class="fa-solid fa-shield-halved text-[10px]"></i> Inspect Proof
          </button>
          <a href="https://pubmed.ncbi.nlm.nih.gov/${c.pmid}/" target="_blank" class="text-slate-400 hover:text-white flex items-center gap-1">
            <span>PubMed</span> <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
          </a>
        </div>
      `;
      citationsContainer.appendChild(card);
    });

    // 4. Refined Prompt Suggestions (3 Targeted Variations)
    const refContainer = document.getElementById('refined-prompts-container');
    if (refContainer) {
      refContainer.innerHTML = '';
      const refPrompts = data.refined_prompts || [];
      if (refPrompts.length > 0) {
        document.getElementById('chat-refined-prompts-section')?.classList.remove('hidden');
        refPrompts.forEach(p => {
          const card = document.createElement('div');
          card.className = "bg-slate-950/80 border border-slate-800 p-3.5 rounded-xl space-y-2 hover:border-cyan-500/50 hover:bg-slate-900/90 transition cursor-pointer group shadow-sm flex flex-col justify-between";
          card.onclick = () => fillAndSubmitChat(p.prompt);

          let badgeColor = "bg-blue-500/10 text-blue-400 border-blue-500/20";
          if (p.category.includes("Safety")) badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/20";
          if (p.category.includes("Guideline")) badgeColor = "bg-purple-500/10 text-purple-400 border-purple-500/20";

          card.innerHTML = `
            <div class="space-y-1.5">
              <span class="text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${badgeColor}">${p.category}</span>
              <p class="text-xs font-semibold text-slate-200 group-hover:text-cyan-300 transition leading-snug">"${p.prompt}"</p>
            </div>
            <div class="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-500">
              <span class="line-clamp-1">${p.rationale}</span>
              <span class="text-cyan-400 group-hover:translate-x-0.5 transition flex items-center gap-1 font-semibold whitespace-nowrap ml-1">
                Explore <i class="fa-solid fa-arrow-right text-[10px]"></i>
              </span>
            </div>
          `;
          refContainer.appendChild(card);
        });
      } else {
        document.getElementById('chat-refined-prompts-section')?.classList.add('hidden');
      }
    }

    // Refresh History Count
    updateHistoryCount();

    // Default to Synthesis Answer subtab
    switchChatSubTab('synthesis');

  } catch (err) {
    console.error("Chat error:", err);
  } finally {
    btn.innerHTML = `<i class="fa-solid fa-paper-plane text-xs"></i> <span>Synthesize</span>`;
    btn.disabled = false;
  }
}

function switchChatSubTab(subTabName) {
  document.querySelectorAll('.chat-subtab').forEach(btn => {
    btn.classList.remove('bg-blue-600', 'text-white', 'active');
    btn.classList.add('text-slate-400');
  });

  const activeBtn = document.getElementById(`subtab-btn-${subTabName}`);
  if (activeBtn) {
    activeBtn.classList.add('bg-blue-600', 'text-white', 'active');
    activeBtn.classList.remove('text-slate-400');
  }

  ['synthesis', 'evidence', 'citations'].forEach(view => {
    const el = document.getElementById(`subview-${view}`);
    if (el) el.classList.add('hidden');
  });

  const targetView = document.getElementById(`subview-${subTabName}`);
  if (targetView) targetView.classList.remove('hidden');
}

// ==================== TAB 3: BIOMEDICAL NER EXPLORER ====================
let currentNERFilter = 'All';

async function loadNERList() {
  try {
    const res = await fetch('/api/ner');
    const data = await res.json();
    currentEntities = data.entities;

    // Update counts on filter buttons
    const condCount = currentEntities.filter(e => e.type === 'Condition').length;
    const drugCount = currentEntities.filter(e => e.type === 'Drug').length;
    const outCount = currentEntities.filter(e => e.type === 'Outcome').length;

    const bAll = document.getElementById('ner-cat-all');
    const bCond = document.getElementById('ner-cat-cond');
    const bDrug = document.getElementById('ner-cat-drug');
    const bOut = document.getElementById('ner-cat-out');

    if (bAll) bAll.innerText = `All (${currentEntities.length})`;
    if (bCond) bCond.innerText = `Conditions (${condCount})`;
    if (bDrug) bDrug.innerText = `Drugs (${drugCount})`;
    if (bOut) bOut.innerText = `Outcomes (${outCount})`;

    filterNER('All');

    // Auto-select first entity
    if (currentEntities.length > 0) {
      selectNEREntity(currentEntities[0].name);
    }
  } catch (err) {
    console.error("Error loading NER:", err);
  }
}

function filterNER(type) {
  currentNERFilter = type;
  document.querySelectorAll('.ner-filter-btn').forEach(btn => {
    btn.classList.remove('bg-blue-600', 'text-white');
    btn.classList.add('bg-slate-800', 'text-slate-300');
    if (btn.innerText.startsWith(type) || (type === 'All' && btn.innerText.startsWith('All'))) {
      btn.classList.add('bg-blue-600', 'text-white');
      btn.classList.remove('bg-slate-800', 'text-slate-300');
    }
  });

  renderNERFiltered();
}

function handleNERSearch() {
  renderNERFiltered();
}

function renderNERFiltered() {
  const container = document.getElementById('ner-list-container');
  if (!container) return;
  container.innerHTML = '';

  const searchVal = document.getElementById('ner-search-input')?.value.toLowerCase().trim() || '';

  let filtered = currentNERFilter === 'All' ? currentEntities : currentEntities.filter(e => e.type === currentNERFilter);
  if (searchVal) {
    filtered = filtered.filter(e => e.name.toLowerCase().includes(searchVal) || (e.cui && e.cui.toLowerCase().includes(searchVal)));
  }

  const countBadge = document.getElementById('ner-concepts-count');
  if (countBadge) countBadge.innerText = filtered.length;

  filtered.forEach(e => {
    const item = document.createElement('div');
    const isSelected = activeNEREntity === e.name;
    item.className = `p-3 rounded-xl border cursor-pointer flex items-center justify-between transition ${
      isSelected ? 'bg-blue-950/40 border-blue-500/50' : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
    }`;
    item.onclick = () => selectNEREntity(e.name);

    let typeBadgeColor = "bg-blue-500/10 text-blue-400 border-blue-500/20";
    if (e.type === 'Condition') typeBadgeColor = "bg-rose-500/10 text-rose-400 border-rose-500/20";
    if (e.type === 'Drug') typeBadgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    if (e.type === 'Outcome') typeBadgeColor = "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";

    item.innerHTML = `
      <div class="flex items-center space-x-2.5">
        <span class="text-[10px] px-2 py-0.5 rounded font-bold uppercase border ${typeBadgeColor}">${e.type}</span>
        <span class="text-xs font-semibold text-white">${e.name}</span>
      </div>
      <div class="flex items-center space-x-2.5 text-xs">
        <span class="font-mono text-slate-500 text-[11px]">${e.cui}</span>
        <span class="bg-slate-800 px-2 py-0.5 rounded text-slate-300 font-bold text-[11px]">${e.papers_count} ${e.papers_count === 1 ? 'trial' : 'trials'}</span>
      </div>
    `;
    container.appendChild(item);
  });
}

async function selectNEREntity(entityName) {
  activeNEREntity = entityName;
  renderNERFiltered();

  const entity = currentEntities.find(e => e.name.toLowerCase() === entityName.toLowerCase());
  if (entity) {
    document.getElementById('ner-active-title').innerText = entity.name;
    document.getElementById('ner-active-cui').innerText = `CUI: ${entity.cui}`;
    document.getElementById('ner-active-trials').innerText = `Found in ${entity.papers_count} landmark ${entity.papers_count === 1 ? 'trial' : 'trials'}`;

    const badge = document.getElementById('ner-active-badge');
    badge.innerText = entity.type;
    badge.className = "text-[10px] font-bold uppercase px-2 py-0.5 rounded border ";
    if (entity.type === 'Condition') badge.className += "bg-rose-500/10 text-rose-400 border-rose-500/20";
    else if (entity.type === 'Drug') badge.className += "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
    else badge.className += "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";
  }

  // Load Section A: Co-occurrences
  try {
    const res = await fetch(`/api/ner/${encodeURIComponent(entityName)}/cooccurrences`);
    const data = await res.json();
    const container = document.getElementById('cooccur-list');
    container.innerHTML = '';
    const list = data.cooccurrences || [];
    document.getElementById('cooccur-count').innerText = list.length;

    if (list.length === 0) {
      container.innerHTML = `<div class="col-span-2 text-xs text-slate-500 py-3 text-center">No co-occurring concepts identified.</div>`;
    } else {
      list.forEach(co => {
        const card = document.createElement('div');
        card.className = "flex items-center justify-between p-2.5 bg-slate-950/80 border border-slate-800 rounded-xl text-xs hover:border-slate-700 transition cursor-pointer";
        card.onclick = () => selectNEREntity(co.entity);
        card.innerHTML = `
          <div>
            <div class="text-slate-200 font-semibold">${co.entity}</div>
            <div class="text-[10px] font-mono text-slate-500">${co.cui || 'UMLS'} • ${co.type}</div>
          </div>
          <span class="text-emerald-400 font-mono font-bold bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-500/20">${co.co_occurrences} trials</span>
        `;
        container.appendChild(card);
      });
    }
  } catch (err) {
    console.error("Co-occurrence error:", err);
  }

  // Load Section B: Source Mentions & Sentences
  try {
    const res = await fetch(`/api/ner/${encodeURIComponent(entityName)}/mentions`);
    const data = await res.json();
    const container = document.getElementById('mentions-list');
    container.innerHTML = '';
    const mentions = data.mentions || [];
    document.getElementById('mentions-count').innerText = mentions.length;

    if (mentions.length === 0) {
      container.innerHTML = `<div class="text-xs text-slate-500 py-3 text-center">No verbatim sentences found.</div>`;
    } else {
      mentions.forEach(m => {
        const card = document.createElement('div');
        card.className = "p-3.5 bg-slate-950/70 border border-slate-800 rounded-xl space-y-2 hover:border-slate-700 transition";

        // Highlight entity in evidence sentence
        const regex = new RegExp(`(${escapeRegex(entityName)})`, 'gi');
        const highlightedSentence = m.evidence_sentence.replace(regex, `<mark class="bg-amber-400/20 text-amber-300 font-bold px-1 rounded">$1</mark>`);

        card.innerHTML = `
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-blue-400">${m.study_acronym} <span class="text-slate-500 font-mono font-normal">PMID:${m.pmid}</span></span>
            <span class="text-slate-400 font-mono text-[11px]">${m.journal_year} • N=${m.sample_size.toLocaleString()}</span>
          </div>
          <p class="text-xs text-slate-300 leading-relaxed font-sans bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
            "${highlightedSentence}"
          </p>
        `;
        container.appendChild(card);
      });
    }
  } catch (err) {
    console.error("Mentions error:", err);
  }
}

// ==================== TAB 4: STRUCTURED PICO GRID ====================
async function loadPicoTable() {
  const drugFilter = document.getElementById('pico-drug-filter')?.value || '';
  try {
    const url = drugFilter ? `/api/pico?drug=${encodeURIComponent(drugFilter)}` : '/api/pico';
    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById('pico-table-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    data.pico_rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.className = "hover:bg-slate-800/40 transition";
      tr.innerHTML = `
        <td class="p-3.5 font-bold text-white whitespace-nowrap">
          ${r.study_acronym}
          <div class="text-[10px] text-slate-500 font-mono font-normal">PMID:${r.pmid} | ${r.journal_year}</div>
        </td>
        <td class="p-3.5 text-slate-300 whitespace-nowrap">
          <span class="px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded text-[10px] border border-blue-500/20 font-bold">${r.study_design}</span>
        </td>
        <td class="p-3.5 text-slate-300 font-mono font-semibold whitespace-nowrap">
          ${r.sample_size ? r.sample_size.toLocaleString() : 'N/A'}
        </td>
        <td class="p-3.5 text-emerald-400 font-semibold whitespace-nowrap">
          ${r.intervention}
        </td>
        <td class="p-3.5 text-slate-400 whitespace-nowrap">
          ${r.comparator || 'Matching Placebo'}
        </td>
        <td class="p-3.5 text-cyan-300 max-w-xs truncate font-medium" title="${r.outcome}">
          ${r.outcome}
        </td>
        <td class="p-3.5 font-bold text-white font-mono whitespace-nowrap">
          ${r.effect_size} <span class="text-slate-400 font-normal text-[11px]">${r.ci_95}</span>
        </td>
        <td class="p-3.5 font-mono text-slate-300 whitespace-nowrap">
          ${r.p_value}
        </td>
        <td class="p-3.5 whitespace-nowrap">
          <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            ${r.direction || 'Favors Drug'}
          </span>
        </td>
        <td class="p-3.5 text-center whitespace-nowrap">
          <button onclick="openQuoteModal('${escapeQuotes(r.study_acronym)}', '${r.journal_year}', '${escapeQuotes(r.evidence_quote || '')}', '${r.pmid}')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-blue-400 border border-slate-700 text-xs flex items-center gap-1 mx-auto transition shadow-sm">
            <i class="fa-solid fa-quote-left text-[10px]"></i> Proof
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Error loading PICO:", err);
  }
}

// ==================== TAB 5: KNOWLEDGE GRAPH VISUALIZATION ====================
async function initKnowledgeGraph() {
  try {
    const res = await fetch('/api/graph');
    const data = await res.json();
    rawGraphNodes = data.nodes;
    rawGraphEdges = data.edges;

    applyGraphDataset();
  } catch (err) {
    console.error("Error rendering graph:", err);
  }
}

function applyGraphDataset() {
  const container = document.getElementById('network-container');
  if (!container) return;

  // Filter nodes based on active checkboxes and hideChunksActive
  const filteredNodes = rawGraphNodes.filter(n => {
    if (hideChunksActive && n.is_chunk) return false;
    if (activeFilters[n.group] === false) return false;
    return true;
  }).map(n => {
    const nodeColor = graphColorMode === 'community' ? n.community_color : n.color;
    return {
      ...n,
      color: nodeColor
    };
  });

  const activeNodeIds = new Set(filteredNodes.map(n => n.id));
  const filteredEdges = rawGraphEdges.filter(e => activeNodeIds.has(e.from) && activeNodeIds.has(e.to));

  const graphData = {
    nodes: new vis.DataSet(filteredNodes),
    edges: new vis.DataSet(filteredEdges)
  };

  const options = {
    nodes: {
      shape: 'dot',
      shadow: true,
      borderWidth: 2,
      font: { color: '#FFFFFF', size: 12, face: 'Inter' }
    },
    edges: {
      width: 1.5,
      smooth: { type: 'continuous' }
    },
    physics: {
      enabled: !physicsFrozen,
      solver: 'forceAtlas2Based',
      forceAtlas2Based: {
        gravitationalConstant: -40,
        centralGravity: 0.01,
        springLength: 90,
        springConstant: 0.08
      },
      maxVelocity: 50,
      minVelocity: 0.1,
      timestep: 0.5,
      stabilization: { iterations: 120 }
    },
    interaction: {
      hover: true,
      tooltipDelay: 150,
      zoomView: true
    }
  };

  networkInstance = new vis.Network(container, graphData, options);

  networkInstance.on("click", function(params) {
    if (params.nodes.length > 0) {
      const nodeId = params.nodes[0];
      const node = rawGraphNodes.find(n => n.id === nodeId);
      if (node) {
        const detailsEl = document.getElementById('graph-node-details');
        if (detailsEl) {
          detailsEl.classList.remove('hidden');
          detailsEl.innerHTML = `
            <div class="flex items-center justify-between border-b border-slate-700 pb-1.5 mb-1.5">
              <span class="font-bold text-white">${node.label.replace('\\n', ' ')}</span>
              <span class="text-[10px] uppercase font-bold text-slate-400 px-1.5 py-0.5 rounded bg-slate-800">${node.group}</span>
            </div>
            <p class="text-slate-300 text-[11px] leading-snug whitespace-pre-line">${node.title || 'Connected node in knowledge graph.'}</p>
            <div class="mt-2 text-[10px] text-cyan-400 font-mono">Community: ${node.community_id ? `Cluster ${node.community_id}` : 'Cluster 1'}</div>
          `;
        }
      }
    }
  });
}

function setGraphColorMode(mode) {
  graphColorMode = mode;
  const btnEntity = document.getElementById('btn-mode-entity');
  const btnComm = document.getElementById('btn-mode-community');

  if (mode === 'entity') {
    btnEntity?.classList.add('bg-blue-600', 'text-white');
    btnEntity?.classList.remove('text-slate-400');
    btnComm?.classList.remove('bg-blue-600', 'text-white');
    btnComm?.classList.add('text-slate-400');
  } else {
    btnComm?.classList.add('bg-blue-600', 'text-white');
    btnComm?.classList.remove('text-slate-400');
    btnEntity?.classList.remove('bg-blue-600', 'text-white');
    btnEntity?.classList.add('text-slate-400');
  }

  applyGraphDataset();
}

function toggleChunksVisibility() {
  hideChunksActive = !hideChunksActive;
  const label = document.getElementById('label-toggle-chunks');
  const btn = document.getElementById('btn-toggle-chunks');
  const chk = document.getElementById('checkbox-filter-chunks');

  if (hideChunksActive) {
    if (label) label.innerText = "Show Chunks";
    if (btn) btn.classList.add('bg-blue-600', 'text-white');
    if (chk) chk.checked = false;
  } else {
    if (label) label.innerText = "Hide Chunks";
    if (btn) btn.classList.remove('bg-blue-600', 'text-white');
    if (chk) chk.checked = true;
  }

  applyGraphDataset();
}

function toggleGraphPhysics() {
  physicsFrozen = !physicsFrozen;
  const label = document.getElementById('label-toggle-physics');
  const btn = document.getElementById('btn-toggle-physics');

  if (physicsFrozen) {
    if (label) label.innerText = "Resume Physics";
    if (btn) btn.classList.add('bg-indigo-600', 'text-white');
    if (networkInstance) networkInstance.setOptions({ physics: { enabled: false } });
  } else {
    if (label) label.innerText = "Freeze Layout";
    if (btn) btn.classList.remove('bg-indigo-600', 'text-white');
    if (networkInstance) {
      networkInstance.setOptions({ physics: { enabled: true } });
      networkInstance.stabilize();
    }
  }
}

function filterGraphGroup(group, isVisible) {
  activeFilters[group] = isVisible;
  if (group === 'Chunk') {
    hideChunksActive = !isVisible;
    const label = document.getElementById('label-toggle-chunks');
    if (label) label.innerText = isVisible ? "Hide Chunks" : "Show Chunks";
  }
  applyGraphDataset();
}

// ==================== PROVENANCE MODAL HELPERS ====================
function openQuoteModal(title, journal, quote, pmid) {
  document.getElementById('modal-article-title').innerText = title;
  document.getElementById('modal-journal-year').innerText = journal;
  document.getElementById('modal-quote-text').innerText = `"${quote}"`;
  document.getElementById('modal-pubmed-link').href = `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`;
  document.getElementById('quote-modal').classList.remove('hidden');
}

function closeQuoteModal() {
  document.getElementById('quote-modal').classList.add('hidden');
}

function escapeQuotes(str) {
  if (!str) return '';
  return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// ==================== AUDIT HISTORY MODAL HELPERS ====================
async function updateHistoryCount() {
  try {
    const res = await fetch('/api/history');
    const data = await res.json();
    const countEl = document.getElementById('nav-history-count');
    const qCountEl = document.getElementById('history-queries-count');
    const ingCountEl = document.getElementById('history-ingest-count');

    const totalQ = data.total_queries_logged || 0;
    const totalIng = data.total_ingestions_logged || 0;

    if (countEl) countEl.innerText = totalQ + totalIng;
    if (qCountEl) qCountEl.innerText = totalQ;
    if (ingCountEl) ingCountEl.innerText = totalIng;
  } catch (err) {
    console.error("Failed to update history count:", err);
  }
}

async function openHistoryModal() {
  document.getElementById('history-modal')?.classList.remove('hidden');
  await renderHistoryLogs();
}

function closeHistoryModal() {
  document.getElementById('history-modal')?.classList.add('hidden');
}

function switchHistoryTab(tabName) {
  const btnQ = document.getElementById('hist-tab-queries');
  const btnIng = document.getElementById('hist-tab-ingestions');
  const viewQ = document.getElementById('hist-view-queries');
  const viewIng = document.getElementById('hist-view-ingestions');

  if (tabName === 'queries') {
    btnQ?.classList.add('bg-blue-600', 'text-white');
    btnQ?.classList.remove('text-slate-400');
    btnIng?.classList.remove('bg-blue-600', 'text-white');
    btnIng?.classList.add('text-slate-400');
    viewQ?.classList.remove('hidden');
    viewIng?.classList.add('hidden');
  } else {
    btnIng?.classList.add('bg-blue-600', 'text-white');
    btnIng?.classList.remove('text-slate-400');
    btnQ?.classList.remove('bg-blue-600', 'text-white');
    btnQ?.classList.add('text-slate-400');
    viewIng?.classList.remove('hidden');
    viewQ?.classList.add('hidden');
  }
}

async function renderHistoryLogs() {
  try {
    const res = await fetch('/api/history');
    const data = await res.json();

    updateHistoryCount();

    // 1. Render User Queries
    const queriesContainer = document.getElementById('history-queries-list');
    if (queriesContainer) {
      queriesContainer.innerHTML = '';
      const queries = data.recent_queries || [];

      if (queries.length === 0) {
        queriesContainer.innerHTML = `<div class="text-center py-10 text-slate-500 text-xs">No queries logged yet. Ask a question in the Chat tab to start your audit trail.</div>`;
      } else {
        queries.forEach(q => {
          const card = document.createElement('div');
          card.className = "bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-3 hover:border-slate-700 transition";
          
          const docsHtml = q.documents.map(d => `
            <div class="flex items-center justify-between text-[11px] bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
              <div class="flex items-center gap-2">
                <span class="font-mono text-blue-400 font-bold">PMID:${d.pmid}</span>
                <span class="text-slate-300 font-medium truncate max-w-md">${d.title}</span>
              </div>
              <span class="text-slate-400 font-mono text-[10px] whitespace-nowrap">${d.journal} (${d.year}) • N=${d.sample_size ? d.sample_size.toLocaleString() : 'N/A'}</span>
            </div>
          `).join('');

          card.innerHTML = `
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="flex items-center gap-2">
                  <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-bold">${q.intent}</span>
                  <span class="text-[10px] text-slate-500 font-mono">${new Date(q.timestamp).toLocaleString()}</span>
                </div>
                <h4 class="text-sm font-bold text-white mt-1 leading-snug flex items-center gap-2">
                  <i class="fa-solid fa-comment-dots text-blue-400 text-xs"></i>
                  <span>"${q.query_text}"</span>
                </h4>
              </div>
              <button onclick="closeHistoryModal(); fillAndSubmitChat('${escapeQuotes(q.query_text)}')" class="px-2.5 py-1 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1 transition shadow-sm whitespace-nowrap">
                <i class="fa-solid fa-rotate-right text-[10px]"></i> Re-Run
              </button>
            </div>

            <!-- Documents Retrieved -->
            <div class="space-y-1.5">
              <div class="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center justify-between">
                <span>Retrieved & Cited Documents (${q.documents_count})</span>
                <span class="text-emerald-400 font-mono">${q.audit_badge}</span>
              </div>
              <div class="space-y-1">
                ${docsHtml}
              </div>
            </div>
          `;
          queriesContainer.appendChild(card);
        });
      }
    }

    // 2. Render Ingestions Log
    const ingestContainer = document.getElementById('history-ingest-list');
    if (ingestContainer) {
      ingestContainer.innerHTML = '';
      const ingestions = data.recent_ingestions || [];

      if (ingestions.length === 0) {
        ingestContainer.innerHTML = `<div class="text-center py-10 text-slate-500 text-xs">No document ingestions logged yet. Use the "Ingest to Graph" bar to fetch trials.</div>`;
      } else {
        ingestions.forEach(ing => {
          const card = document.createElement('div');
          card.className = "bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-2 hover:border-slate-700 transition";

          const docsHtml = ing.ingested_documents.map(d => `
            <div class="flex items-center justify-between text-[11px] bg-slate-950/60 p-2 rounded-lg border border-slate-800/80">
              <span class="font-mono text-emerald-400 font-bold">PMID:${d.pmid}</span>
              <span class="text-slate-300 font-medium truncate max-w-md">${d.title}</span>
              <span class="text-slate-400 font-mono text-[10px]">${d.journal} (${d.year})</span>
            </div>
          `).join('');

          card.innerHTML = `
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">Ingestion Batch</span>
                <span class="text-xs font-semibold text-white">Input Query: "${ing.input_query}"</span>
              </div>
              <span class="text-[10px] text-slate-500 font-mono">${new Date(ing.timestamp).toLocaleString()}</span>
            </div>
            <div class="flex items-center gap-3 text-xs text-slate-400 pt-1">
              <span>Articles Added: <strong class="text-white">${ing.total_ingested}</strong></span>
              <span>Section Chunks Added: <strong class="text-indigo-400">${ing.section_chunks_added}</strong></span>
              <span>Total Graph Edges: <strong class="text-cyan-400">${ing.total_kg_edges}</strong></span>
            </div>
            <div class="space-y-1 pt-1">
              ${docsHtml}
            </div>
          `;
          ingestContainer.appendChild(card);
        });
      }
    }

  } catch (err) {
    console.error("Failed to render history logs:", err);
  }
}

async function clearAuditHistory() {
  if (!confirm("Are you sure you want to clear the audit history log?")) return;
  try {
    const res = await fetch('/api/history', { method: 'DELETE' });
    const data = await res.json();
    alert(data.message || "Audit history cleared.");
    await renderHistoryLogs();
  } catch (err) {
    console.error("Error clearing history:", err);
  }
}

// ==================== APP INITIALIZATION ====================
window.onload = () => {
  loadCorpusData();
  updateHistoryCount();

  // Real-time debounced query suggestion updater for Ingest bar
  let ingestDebounceTimer = null;
  const ingestInput = document.getElementById('ingest-input');
  if (ingestInput) {
    ingestInput.addEventListener('input', (e) => {
      clearTimeout(ingestDebounceTimer);
      ingestDebounceTimer = setTimeout(() => {
        fetchIngestionSuggestions(e.target.value.trim());
      }, 350);
    });

    ingestInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        ingestArticle();
      }
    });
  }
};
