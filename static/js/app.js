/**
 * Grammar-Based Pattern Recognition Engine — Frontend Client Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // State Management
  const state = {
    activeTab: "playground",
    activeGrammar: "email",
    activeVisView: "svg",
    samples: null,
    currentResult: null,
    batchData: null
  };

  // DOM Element Selectors
  const patternInput = document.getElementById("pattern-input");
  const charCount = document.getElementById("char-count");
  const clearInputBtn = document.getElementById("clear-input");
  const btnValidate = document.getElementById("btn-validate");
  const grammarBadge = document.getElementById("grammar-badge");
  const sampleChipsContainer = document.getElementById("sample-chips");
  const tokenStrip = document.getElementById("token-strip");

  // Verdict Hero Elements
  const verdictHero = document.getElementById("verdict-hero");
  const verdictBadge = document.getElementById("verdict-badge");
  const errorBadge = document.getElementById("error-badge");
  const verdictPattern = document.getElementById("verdict-pattern");
  const verdictError = document.getElementById("verdict-error");
  const matchedSection = document.getElementById("matched-section");
  const matchedGrid = document.getElementById("matched-grid");

  // Tree View Elements
  const treeSvgContainer = document.getElementById("tree-svg-container");
  const treeAsciiContainer = document.getElementById("tree-ascii-container");
  const btnVisSvg = document.getElementById("btn-vis-svg");
  const btnVisAscii = document.getElementById("btn-vis-ascii");

  // Batch Elements
  const batchInputArea = document.getElementById("batch-input-area");
  const btnRunBatch = document.getElementById("btn-run-batch");
  const btnLoadDefaultBatch = document.getElementById("btn-load-default-batch");
  const batchStatusText = document.getElementById("batch-status-text");
  const batchStatTotal = document.getElementById("batch-stat-total");
  const batchStatAccepted = document.getElementById("batch-stat-accepted");
  const batchStatRejected = document.getElementById("batch-stat-rejected");
  const batchStatRate = document.getElementById("batch-stat-rate");
  const batchTableBody = document.getElementById("batch-table-body");

  // Grammar Explorer Elements
  const grammarEmailCode = document.getElementById("grammar-email-code");
  const grammarDateCode = document.getElementById("grammar-date-code");

  // Benchmark Elements
  const benchSvgContainer = document.getElementById("bench-svg-container");
  const btnReBenchmark = document.getElementById("btn-re-benchmark");
  const statR2 = document.getElementById("stat-r2");
  const statR = document.getElementById("stat-r");
  const statSlope = document.getElementById("stat-slope");
  const badgeR2 = document.getElementById("badge-r2");

  // --- 1. Tab Navigation ---
  const navTabBtns = document.querySelectorAll(".nav-tab-btn");
  navTabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTab = btn.getAttribute("data-tab");
      switchTab(targetTab);
    });
  });

  function switchTab(tabId) {
    state.activeTab = tabId;
    navTabBtns.forEach(b => b.classList.toggle("active", b.getAttribute("data-tab") === tabId));
    document.querySelectorAll(".tab-content").forEach(c => c.classList.toggle("active", c.id === `tab-${tabId}`));

    if (tabId === "grammars") {
      loadGrammarRules();
    } else if (tabId === "benchmarks") {
      loadBenchmarkData();
    }
  }

  // --- 2. Grammar Switcher ---
  const btnGrammarEmail = document.getElementById("btn-grammar-email");
  const btnGrammarDate = document.getElementById("btn-grammar-date");

  btnGrammarEmail.addEventListener("click", () => setGrammar("email"));
  btnGrammarDate.addEventListener("click", () => setGrammar("date"));

  function setGrammar(grammarType) {
    state.activeGrammar = grammarType;
    btnGrammarEmail.classList.toggle("active", grammarType === "email");
    btnGrammarDate.classList.toggle("active", grammarType === "date");

    grammarBadge.textContent = `CFG Model: ${grammarType === "email" ? "Email" : "Calendar Date"}`;
    patternInput.placeholder = grammarType === "email" ? "e.g. dhanshree01@gmail.com" : "e.g. 2026-09-10 or 15/08/1947";

    renderSampleChips();

    // Default sample for grammar
    const defaultSample = grammarType === "email" ? "dhanshree01@gmail.com" : "2026-09-10";
    patternInput.value = defaultSample;
    updateCharCount();
    validatePattern(defaultSample);
  }

  // --- 3. Input Handling ---
  patternInput.addEventListener("input", updateCharCount);
  patternInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      validateCurrentInput();
    }
  });

  clearInputBtn.addEventListener("click", () => {
    patternInput.value = "";
    patternInput.focus();
    updateCharCount();
  });

  btnValidate.addEventListener("click", validateCurrentInput);

  function updateCharCount() {
    charCount.textContent = `${patternInput.value.length} chars`;
  }

  function validateCurrentInput() {
    const inputVal = patternInput.value.trim();
    validatePattern(inputVal);
  }

  // --- 4. API: Pattern Validation ---
  async function validatePattern(patternStr) {
    btnValidate.innerHTML = `<span>⏳</span> Parsing...`;
    btnValidate.disabled = true;

    try {
      const resp = await fetch("/api/validate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input: patternStr, grammar: state.activeGrammar })
      });
      const data = await resp.json();
      state.currentResult = data;
      renderValidationResult(data);
    } catch (err) {
      console.error("Validation error:", err);
    } finally {
      btnValidate.innerHTML = `<span>✨</span> Parse & Derive Pattern`;
      btnValidate.disabled = false;
    }
  }

  function renderValidationResult(data) {
    verdictPattern.textContent = data.input || "(empty string)";

    // 1. Hero Card Verdict State
    if (data.is_valid) {
      verdictHero.className = "verdict-hero accepted";
      verdictBadge.innerHTML = `<span>✔</span> ACCEPTED`;
      errorBadge.style.display = "none";
      verdictError.style.display = "none";
      matchedSection.style.display = "block";

      // Render matched sub-components
      matchedGrid.innerHTML = "";
      const entries = Object.entries(data.matched_components || {});
      if (entries.length > 0) {
        entries.forEach(([key, val]) => {
          const card = document.createElement("div");
          card.className = "comp-card";
          card.innerHTML = `
            <span class="comp-name">${key}</span>
            <span class="comp-val">${escapeHtml(val)}</span>
          `;
          matchedGrid.appendChild(card);
        });
      }
    } else {
      verdictHero.className = "verdict-hero rejected";
      verdictBadge.innerHTML = `<span>✕</span> REJECTED`;
      errorBadge.textContent = data.error_code || "SYNTAX_ERROR";
      errorBadge.style.display = "inline-block";
      verdictError.textContent = data.error_message || "Pattern does not conform to grammar rules.";
      verdictError.style.display = "block";
      matchedSection.style.display = "none";
    }

    // 2. Token Stream Display
    tokenStrip.innerHTML = "";
    if (data.tokens && data.tokens.length > 0) {
      data.tokens.forEach(tok => {
        const badge = document.createElement("div");
        badge.className = `token-badge ${tok.type === 'INVALID' ? 'token-invalid' : ''}`;
        badge.innerHTML = `
          <span class="token-type">${tok.type}</span>
          <span class="token-val">"${escapeHtml(tok.value)}"</span>
          <span class="token-pos">@${tok.pos}</span>
        `;
        tokenStrip.appendChild(badge);
      });
    } else {
      tokenStrip.innerHTML = `<span style="color: var(--text-muted); font-size: 0.85rem;">No terminal tokens generated.</span>`;
    }

    // 3. Tree Visualizer Display
    if (data.is_valid && data.svg_content) {
      treeSvgContainer.innerHTML = data.svg_content;
    } else if (data.is_valid) {
      treeSvgContainer.innerHTML = `
        <div class="tree-empty-state">
          <div class="icon">🌿</div>
          <p>Parse tree derivation exists.</p>
        </div>`;
    } else {
      treeSvgContainer.innerHTML = `
        <div class="tree-empty-state">
          <div class="icon" style="color: #F87171;">✕</div>
          <p style="color: #F87171;">Derivation Failed — No valid parse tree constructed.</p>
        </div>`;
    }

    if (data.ascii_tree) {
      treeAsciiContainer.textContent = data.ascii_tree;
    } else {
      treeAsciiContainer.textContent = "No derivation tree available for rejected input.";
    }
  }

  // --- 5. Tree View Switcher (SVG vs ASCII) ---
  btnVisSvg.addEventListener("click", () => setVisView("svg"));
  btnVisAscii.addEventListener("click", () => setVisView("ascii"));

  function setVisView(viewType) {
    state.activeVisView = viewType;
    btnVisSvg.classList.toggle("active", viewType === "svg");
    btnVisAscii.classList.toggle("active", viewType === "ascii");

    if (viewType === "svg") {
      treeSvgContainer.style.display = "flex";
      treeAsciiContainer.style.display = "none";
    } else {
      treeSvgContainer.style.display = "none";
      treeAsciiContainer.style.display = "block";
    }
  }

  // --- 6. Load Sample Chips ---
  async function loadSamples() {
    try {
      const resp = await fetch("/api/samples");
      state.samples = await resp.json();
      renderSampleChips();
    } catch (err) {
      console.error("Failed to load samples:", err);
    }
  }

  function renderSampleChips() {
    if (!state.samples) return;
    const currentSamples = state.samples[state.activeGrammar];
    sampleChipsContainer.innerHTML = "";

    // Valid chips
    currentSamples.valid.forEach(s => {
      const chip = document.createElement("button");
      chip.className = "sample-chip";
      chip.textContent = `✔ ${s.label}`;
      chip.title = `Test: ${s.value}`;
      chip.addEventListener("click", () => {
        patternInput.value = s.value;
        updateCharCount();
        validatePattern(s.value);
      });
      sampleChipsContainer.appendChild(chip);
    });

    // Invalid chips
    currentSamples.invalid.forEach(s => {
      const chip = document.createElement("button");
      chip.className = "sample-chip invalid-chip";
      chip.textContent = `✕ ${s.label}`;
      chip.title = `Test rejection: ${s.value}`;
      chip.addEventListener("click", () => {
        patternInput.value = s.value;
        updateCharCount();
        validatePattern(s.value);
      });
      sampleChipsContainer.appendChild(chip);
    });
  }

  // --- 7. Batch Evaluation ---
  btnRunBatch.addEventListener("click", async () => {
    const rawText = batchInputArea.value;
    if (!rawText.trim()) {
      alert("Please paste at least one pattern in the textarea.");
      return;
    }

    btnRunBatch.disabled = true;
    batchStatusText.textContent = "Processing batch...";

    try {
      const resp = await fetch("/api/batch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: rawText, grammar: state.activeGrammar })
      });
      const data = await resp.json();
      renderBatchResults(data);
      batchStatusText.textContent = `Completed ${data.total} patterns in batch.`;
    } catch (err) {
      console.error("Batch error:", err);
      batchStatusText.textContent = "Batch evaluation failed.";
    } finally {
      btnRunBatch.disabled = false;
    }
  });

  btnLoadDefaultBatch.addEventListener("click", () => {
    batchInputArea.value = [
      "# Sample Pattern Evaluation Dataset",
      "dhanshree01@gmail.com",
      "john.doe@company.org",
      "user_123@sub-domain.co.in",
      "test.name+tag@dev.io",
      "plainaddress",
      "@missinglocal.com",
      "user@.com",
      "user@domain",
      "user@@domain.com",
      "user name@gmail.com"
    ].join("\n");
  });

  function renderBatchResults(data) {
    batchStatTotal.textContent = data.total;
    batchStatAccepted.textContent = data.accepted;
    batchStatRejected.textContent = data.rejected;
    batchStatRate.textContent = `${data.accuracy_rate}%`;

    batchTableBody.innerHTML = "";
    data.results.forEach((r, idx) => {
      const tr = document.createElement("tr");
      const isOk = r.is_valid;
      const verdictHtml = isOk
        ? `<span class="pill-badge pill-green" style="font-size: 0.72rem;">ACCEPTED</span>`
        : `<span class="pill-badge" style="background: var(--status-rejected-bg); color: #F87171; border: 1px solid var(--status-rejected-border); font-size: 0.72rem;">REJECTED</span>`;

      const diagHtml = isOk
        ? `<span style="color: var(--text-muted);">—</span>`
        : `<span class="error-badge-pill" style="font-size: 0.72rem;">${r.error_code}</span>`;

      const detailHtml = isOk
        ? `<span style="color: var(--accent-cyan); font-family: var(--font-mono); font-size: 0.82rem;">${JSON.stringify(r.matched_components)}</span>`
        : `<span style="color: #FCA5A5; font-size: 0.82rem;">${escapeHtml(r.error_message)}</span>`;

      tr.innerHTML = `
        <td style="color: var(--text-muted);">${idx + 1}</td>
        <td style="font-family: var(--font-mono); font-weight: 600;">${escapeHtml(r.input)}</td>
        <td>${verdictHtml}</td>
        <td>${diagHtml}</td>
        <td>${detailHtml}</td>
      `;
      batchTableBody.appendChild(tr);
    });
  }

  // --- 8. Grammar Rules Explorer ---
  async function loadGrammarRules() {
    try {
      const resp = await fetch("/api/grammars");
      const data = await resp.json();
      if (data.email) {
        grammarEmailCode.textContent = data.email.rules;
      }
      if (data.date) {
        grammarDateCode.textContent = data.date.rules;
      }
    } catch (err) {
      console.error("Failed to load grammars:", err);
    }
  }

  // --- 9. Benchmarks Center ---
  async function loadBenchmarkData() {
    benchSvgContainer.innerHTML = `<p style="color: var(--text-muted);">Loading benchmark report...</p>`;
    try {
      const resp = await fetch("/api/benchmark", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scales: [20, 50, 100, 250, 500, 1000, 2500], iterations: 50 })
      });
      const data = await resp.json();
      renderBenchmarkResults(data);
    } catch (err) {
      console.error("Benchmark error:", err);
      benchSvgContainer.innerHTML = `<p style="color: #F87171;">Failed to load benchmark data.</p>`;
    }
  }

  btnReBenchmark.addEventListener("click", () => {
    btnReBenchmark.disabled = true;
    btnReBenchmark.textContent = "⏳ Running Benchmarks...";
    loadBenchmarkData().finally(() => {
      btnReBenchmark.disabled = false;
      btnReBenchmark.textContent = "🔄 Re-Run Live Benchmark";
    });
  });

  function renderBenchmarkResults(data) {
    const analysis = data.complexity_analysis;
    statR2.textContent = analysis.r_squared;
    statR.textContent = analysis.correlation_coefficient_r;
    statSlope.textContent = `${analysis.linear_regression_slope_us_per_char} µs / char`;
    badgeR2.textContent = `R² = ${analysis.r_squared}`;

    // Render an inline SVG chart based on benchmark results
    const results = data.results;
    benchSvgContainer.innerHTML = generateClientSvgChart(results, analysis);
  }

  function generateClientSvgChart(results, analysis) {
    const width = 720;
    const height = 360;
    const ml = 60, mr = 30, mt = 40, mb = 50;
    const pw = width - ml - mr;
    const ph = height - mt - mb;

    const maxX = Math.max(...results.map(r => r.actual_length)) * 1.05;
    const maxY = Math.max(...results.map(r => r.mean_latency_us)) * 1.15;

    const sx = x => ml + (x / maxX) * pw;
    const sy = y => mt + ph - (y / maxY) * ph;

    // Grid lines
    let grid = "";
    for (let i = 0; i <= 4; i++) {
      const vx = (maxX / 4) * i;
      const xPos = sx(vx);
      grid += `<line x1="${xPos}" y1="${mt}" x2="${xPos}" y2="${mt + ph}" stroke="#E2E8F0" stroke-dasharray="3,3" />`;
      grid += `<text x="${xPos}" y="${mt + ph + 18}" font-family="JetBrains Mono" font-size="10" font-weight="600" fill="#64748B" text-anchor="middle">${Math.round(vx)}</text>`;

      const vy = (maxY / 4) * i;
      const yPos = sy(vy);
      grid += `<line x1="${ml}" y1="${yPos}" x2="${ml + pw}" y2="${yPos}" stroke="#E2E8F0" stroke-dasharray="3,3" />`;
      grid += `<text x="${ml - 10}" y="${yPos + 3}" font-family="JetBrains Mono" font-size="10" font-weight="600" fill="#64748B" text-anchor="end">${Math.round(vy)}µs</text>`;
    }

    // Trendline (Linear Regression in Green)
    const x1 = 0, y1 = Math.max(0, analysis.intercept_us);
    const x2 = maxX, y2 = analysis.intercept_us + analysis.linear_regression_slope_us_per_char * maxX;
    const trendline = `<line x1="${sx(x1)}" y1="${sy(y1)}" x2="${sx(x2)}" y2="${sy(y2)}" stroke="#10B981" stroke-width="2.5" stroke-dasharray="6,4" />`;

    // Data points & polyline (in Orange)
    const points = results.map(r => `${sx(r.actual_length)},${sy(r.mean_latency_us)}`).join(" ");
    let circles = "";
    results.forEach(r => {
      const cx = sx(r.actual_length);
      const cy = sy(r.mean_latency_us);
      circles += `<circle cx="${cx}" cy="${cy}" r="5" fill="#F97316" stroke="#FFFFFF" stroke-width="2" />`;
    });

    return `
      <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: auto; font-family: Outfit, sans-serif;">
        <rect width="${width}" height="${height}" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5" rx="10" />
        ${grid}
        <line x1="${ml}" y1="${mt + ph}" x2="${ml + pw}" y2="${mt + ph}" stroke="#94A3B8" stroke-width="1.5" />
        <line x1="${ml}" y1="${mt}" x2="${ml}" y2="${mt + ph}" stroke="#94A3B8" stroke-width="1.5" />
        ${trendline}
        <polyline points="${points}" fill="none" stroke="#F97316" stroke-width="2.5" />
        ${circles}
        <text x="${ml + pw / 2}" y="${height - 12}" font-size="11" font-weight="700" fill="#334155" text-anchor="middle">Input String Length (Characters, n)</text>
        <text transform="rotate(-90)" x="${-mt - ph / 2}" y="20" font-size="11" font-weight="700" fill="#334155" text-anchor="middle">Latency (µs)</text>
      </svg>
    `;
  }

  // --- Utility Helpers ---
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Initial Initialization
  loadSamples();
  validatePattern("dhanshree01@gmail.com");
  btnLoadDefaultBatch.click();
});
