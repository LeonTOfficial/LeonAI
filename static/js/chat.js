/** LEON AI – Chat messaging and SSE streaming */
(function () {
  const { state, $, esc, api, fmtTime, thinkingHtml } = Leon;

  Leon.welcomeHtml = function welcomeHtml() {
    const firstName = String(window.LEON_PROFILE?.first_name || 'Leon').trim() || 'Leon';
    return `<div id="welcome">
      <div class="hero-icon"><span class="dot-logo"></span></div>
      <h1>Hallo ${esc(firstName)}.</h1>
      <p>Wie kann ich dir heute helfen?</p>
      <div class="thinking-line ${state.isStreaming ? 'show' : ''}" id="welcome-thinking">
        <div class="spinner"></div><div class="thinking-pill">LEON denkt nach <span class="dots">•••</span></div>
      </div>
    </div>`;
  };

  Leon.loadMessages = async function loadMessages(quiet = false) {
    if (!state.currentRoomId) {
      state.messages = [];
      state.artifactHistory = [];
      state.artifactHistoryRoomId = null;
      state.activeLeafId = null;
      $('chat-box').innerHTML = Leon.welcomeHtml();
      Leon.renderArtifacts();
      return;
    }
    const data = await api(`/api/rooms/${state.currentRoomId}/messages`);
    if (!data) return;
    state.messages = data;
    await Leon.loadArtifactHistory?.(state.currentRoomId);
    // Set activeLeafId to the latest message if not set or invalid
    if (!state.activeLeafId || !state.messages.find(m => m.id === state.activeLeafId)) {
        state.activeLeafId = state.messages.length ? state.messages[state.messages.length - 1].id : null;
    }
    Leon.renderMessages();
    if (!quiet) setTimeout(Leon.scrollBottom, 50);
  };

  Leon.getActivePath = function() {
    const path = [];
    if (!state.messages.length) return path;
    const temps = state.messages.filter(m => !m.id && m._tempId);
    let curr = state.activeLeafId ? state.messages.find(m => m.id === state.activeLeafId) : null;
    if (!curr && !temps.length) curr = state.messages[state.messages.length - 1];
    while (curr) {
      path.unshift(curr);
      curr = state.messages.find(m => m.id === curr.parent_id);
    }
    temps.forEach(m => path.push(m));
    return path;
  };

  Leon.renderMessages = function renderMessages() {
    const box = $('chat-box');
    Leon.disposeRichCharts();
    if (!state.messages.length && !state.isStreaming) {
      box.innerHTML = Leon.welcomeHtml();
      Leon.renderArtifacts();
      return;
    }
    const path = Leon.getActivePath();
    box.innerHTML = path.map(m => Leon.renderMessage(m)).join('');
    Leon.renderRichBlocks(box);
    Leon.enhanceCodeBlocks(box);
    Leon.sanitizeRelativeImages(box);
    Leon.renderArtifacts();
  };

  window.switchBranch = function(msgId, dir) {
    const msg = state.messages.find(m => m.id === msgId);
    if (!msg) return;
    const siblings = state.messages.filter(m => m.parent_id === msg.parent_id);
    const idx = siblings.findIndex(m => m.id === msgId);
    if (idx === -1) return;
    let newIdx = idx + dir;
    if (newIdx < 0) newIdx = siblings.length - 1;
    if (newIdx >= siblings.length) newIdx = 0;
    
    // Find leaf of this new branch
    let curr = siblings[newIdx];
    while (true) {
        const children = state.messages.filter(m => m.parent_id === curr.id);
        if (!children.length) break;
        curr = children[children.length - 1]; // pick latest child
    }
    state.activeLeafId = curr.id;
    Leon.renderMessages();
  };

  window.editMessage = function(msgId) {
    const msg = state.messages.find(m => m.id === msgId);
    if (!msg) return;
    const input = $('user-input');
    if (!input) return;
    state.editParentId = msg.parent_id ?? null;
    state.activeLeafId = state.editParentId;
    input.value = msg.content || '';
    Leon.autoResize(input);
    Leon.updateCharCount();
    input.focus();
    Leon.renderMessages();
    Leon.toast('Nachricht bearbeiten und senden erzeugt einen neuen Ast.');
  };

  Leon.renderMessage = function renderMessage(m) {
    const role = m.role === 'user' ? 'user' : 'ai';
    const who = role === 'user' ? 'Du' : 'LEON AI';
    const av = role === 'user' 
        ? Leon.avatarMarkup(localStorage.getItem('leon-avatar') || 'dots', true)
        : '<span class="dot-logo small" style="margin-top:2px;"></span>';
    const content = role === 'user' ? esc(m.content) : Leon.renderMarkdown(m.content || '');
    const imageHtml = m.image_b64
      ? `<img class="image-preview" src="${String(m.image_b64).startsWith('data:') ? esc(m.image_b64) : 'data:image/jpeg;base64,' + esc(m.image_b64)}" alt="Hochgeladenes Bild">`
      : '';
    const fav = m.favorite ? 'active' : '';
    
    let branchHtml = '';
    if (m.id) {
        const siblings = state.messages.filter(x => x.parent_id === m.parent_id);
        if (siblings.length > 1) {
            const idx = siblings.findIndex(x => x.id === m.id) + 1;
            branchHtml = `<div class="branch-nav">
                <button class="mini-btn" onclick="switchBranch(${m.id}, -1)">‹</button>
                <span style="font-size:0.6rem; color:var(--muted);">${idx} / ${siblings.length}</span>
                <button class="mini-btn" onclick="switchBranch(${m.id}, 1)">›</button>
            </div>`;
        }
    }

    const actions = role === 'ai'
      ? `<div class="msg-actions">
        <button class="action-btn" onclick="copyMessage(${m.id || 0})">Kopieren</button>
        ${m.id ? `<button class="action-btn ${fav}" onclick="toggleFavorite(${m.id})">Favorit</button>` : ''}
        ${branchHtml}
      </div>`
      : `<div class="msg-actions">
        ${m.id ? `<button class="action-btn" onclick="editMessage(${m.id})">Bearbeiten</button>` : ''}
        ${branchHtml}
      </div>`;

    return `<article class="msg-wrap ${role}" data-msg-id="${m.id || ''}" data-temp-id="${m._tempId || ''}">
      <div class="msg-inner">
        <div class="msg-head"><div class="msg-av av-${role}">${av}</div><div class="msg-who">${who}</div><div class="msg-time">${fmtTime(m.created)}</div></div>
        <div class="msg-content ${role === 'ai' ? 'ai-content' : 'user-content'}">${imageHtml}${content}</div>
        ${actions}
      </div>
    </article>`;
  };

  Leon.renderMarkdown = function renderMarkdown(text) {
    if (window.marked) {
      marked.setOptions({ breaks: true, gfm: true });
      const raw = marked.parse(Leon.expandColorTags(text));
      return window.DOMPurify ? DOMPurify.sanitize(raw, { ADD_ATTR: ['target'] }) : raw;
    }
    return esc(text).replace(/\n/g, '<br>');
  };

  Leon.expandColorTags = function expandColorTags(text) {
    const names = {
      rot: 'red', red: 'red',
      gruen: 'green', grün: 'green', green: 'green',
      blau: 'blue', blue: 'blue',
      gelb: 'yellow', yellow: 'yellow',
      lila: 'purple', purple: 'purple',
      mark: 'mark', marker: 'mark',
    };
    const tagNames = 'rot|red|gruen|grün|green|blau|blue|gelb|yellow|lila|purple|mark|marker';
    const toColor = (value) => names[String(value || '').toLowerCase()] || '';
    const span = (color, content) => `<span class="leon-color-${color}">${content}</span>`;
    let out = String(text || '').replace(
      new RegExp(`\\[(${tagNames})\\]([\\s\\S]*?)\\[\\/(${tagNames})\\]`, 'gi'),
      (match, openName, content, closeName) => {
        const openColor = toColor(openName);
        const closeColor = toColor(closeName);
        if (!openColor || openColor !== closeColor) return match;
        return span(openColor, content);
      },
    );
    out = out.replace(
      new RegExp(`\\[(${tagNames})\\](\\*\\*[^*\\n]+?\\*\\*|__[^_\\n]+?__|\\*[^*\\n]+?\\*|_[^_\\n]+?_|[^\\s\\[\\]<>,.;:!?]+)`, 'gi'),
      (match, name, content) => {
        const color = toColor(name);
        return color ? span(color, content) : match;
      },
    );
    out = out.replace(
      new RegExp(`\\[(${tagNames})\\]\\s+([^\\n<]+)`, 'gi'),
      (match, name, content) => {
        const color = toColor(name);
        return color ? span(color, content) : match;
      },
    );
    return out;
  };

  /** Verhindert 404-Requests für relative Bildpfade aus KI-generiertem HTML. */
  Leon.sanitizeRelativeImages = function sanitizeRelativeImages(root) {
    if (!root) return;
    root.querySelectorAll('img[src]').forEach((img) => {
      const src = (img.getAttribute('src') || '').trim();
      if (!src || /^(https?:|data:|\/static\/)/i.test(src)) return;
      img.removeAttribute('src');
      img.alt = img.alt || 'Bild nicht verfügbar (lokaler Pfad aus KI-Antwort)';
      img.classList.add('image-unavailable');
    });
  };

  Leon.disposeRichCharts = function disposeRichCharts() {
    (state.richCharts || []).forEach((chart) => {
      try { chart.destroy(); } catch {}
    });
    state.richCharts = [];
  };

  function codeBlockLang(code) {
    const classes = [...code.classList, ...(code.parentElement?.classList || [])];
    const langClass = classes.find(c => c.startsWith('language-')) || classes.find(c => c.startsWith('lang-')) || '';
    const explicit = code.dataset.language || code.parentElement?.dataset.language || '';
    return (explicit || langClass.replace(/^language-/, '').replace(/^lang-/, '') || '').toLowerCase().trim();
  }

  const MERMAID_LANGS = new Set(['mermaid', 'mmd', 'diagram', 'diagramm', 'flussdiagramm', 'flowchart', 'graph']);
  const CHART_LANGS = new Set([
    'chart', 'chartjs', 'chart-js', 'leon-chart', 'json-chart', 'chart-codeblock',
    'bar', 'barchart', 'bar-chart', 'balkendiagramm', 'line', 'linechart', 'line-chart', 'pie', 'doughnut',
  ]);
  const RICH_LIBS = {
    mermaid: 'https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.9.1/mermaid.min.js',
    chart: 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js',
  };
  const scriptPromises = {};

  function waitUntilReady(isReady, timeout = 8000) {
    const started = Date.now();
    return new Promise((resolve, reject) => {
      const tick = () => {
        if (isReady()) return resolve();
        if (Date.now() - started > timeout) return reject(new Error('Bibliothek wurde geladen, ist aber nicht verfügbar.'));
        setTimeout(tick, 60);
      };
      tick();
    });
  }

  function loadScriptOnce(key, src, isReady) {
    if (isReady()) return Promise.resolve();
    if (scriptPromises[key]) return scriptPromises[key];
    scriptPromises[key] = new Promise((resolve, reject) => {
      const existing = document.querySelector(`script[src="${src}"]`);
      const script = existing || document.createElement('script');
      const done = () => waitUntilReady(isReady).then(resolve, reject);
      script.addEventListener('load', done, { once: true });
      script.addEventListener('error', () => reject(new Error(`${key} konnte nicht geladen werden.`)), { once: true });
      if (!existing) {
        script.src = src;
        script.async = true;
        document.head.appendChild(script);
      } else {
        setTimeout(done, 0);
      }
    }).catch((err) => {
      delete scriptPromises[key];
      throw err;
    });
    return scriptPromises[key];
  }

  function ensureMermaidLoaded() {
    return loadScriptOnce('Mermaid', RICH_LIBS.mermaid, () => !!window.mermaid?.run);
  }

  function ensureChartLoaded() {
    return loadScriptOnce('Chart.js', RICH_LIBS.chart, () => typeof window.Chart === 'function');
  }

  function decodeHtmlEntities(text) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = String(text || '');
    return textarea.value;
  }

  function normalizeMermaidSource(text) {
    let source = decodeHtmlEntities(text)
      .replace(/\r\n?/g, '\n')
      .replace(/\u00a0/g, ' ')
      .trim();
    source = source.replace(/^\s*(diagramm|diagram|flussdiagramm)\s*\n/i, '');
    source = source.replace(/(-->|---|==>|-.->)\s*\|([^|\n]+)\|\s*>\s*/g, '$1|$2| ');
    source = source.replace(/(\[[^\]\n]*\])([A-Za-z][\w-]*)\s*(-->|---|==>|-.->)/g, '$1\n$2 $3');
    source = source.replace(/\n{3,}/g, '\n\n');
    if (!/^\s*(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph)\b/i.test(source)
      && /(-->|---|==>|-.->)/.test(source)) {
      source = `flowchart TD\n${source}`;
    }
    return source;
  }

  function parseChartCandidate(text) {
    try {
      const parsed = JSON.parse(String(text || '').trim());
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return null;
      const data = parsed.data || {};
      const hasDatasets = Array.isArray(data.datasets) || Array.isArray(parsed.datasets);
      const hasLabels = Array.isArray(data.labels) || Array.isArray(parsed.labels);
      const hasType = typeof parsed.type === 'string';
      return (hasDatasets && (hasLabels || hasType)) ? parsed : null;
    } catch {
      return null;
    }
  }

  function isMermaidLang(lang) {
    return MERMAID_LANGS.has(String(lang || '').toLowerCase());
  }

  function isChartLang(lang, text = '') {
    const clean = String(lang || '').toLowerCase();
    return CHART_LANGS.has(clean) || ((clean === 'json' || clean === '') && !!parseChartCandidate(text));
  }

  function richBlock(title) {
    const wrap = document.createElement('div');
    wrap.className = 'rich-block';
    const head = document.createElement('div');
    head.className = 'rich-block-head';
    head.textContent = title;
    wrap.appendChild(head);
    return wrap;
  }

  function showRichError(wrap, message) {
    const body = document.createElement('div');
    body.className = 'rich-error';
    body.textContent = message;
    wrap.appendChild(body);
  }

  Leon.renderRichBlocks = function renderRichBlocks(root) {
    if (!root) return;
    root.querySelectorAll('pre > code').forEach((code) => {
      if (code.closest('.code-wrap') || code.closest('.rich-block')) return;
      const lang = codeBlockLang(code);
      if (isMermaidLang(lang)) {
        Leon.renderMermaidBlock(code);
      } else if (isChartLang(lang, code.innerText)) {
        Leon.renderChartBlock(code);
      }
    });
  };

  Leon.renderMermaidBlock = function renderMermaidBlock(code) {
    const pre = code.parentElement;
    if (!pre?.parentNode) return;
    const source = normalizeMermaidSource(code.innerText);
    const wrap = richBlock('Diagramm');
    const body = document.createElement('div');
    body.className = 'rich-mermaid-body';
    const diagram = document.createElement('div');
    diagram.className = 'mermaid';
    diagram.textContent = source;
    body.appendChild(diagram);
    wrap.appendChild(body);
    pre.parentNode.replaceChild(wrap, pre);

    const fail = (err) => {
      if (body.isConnected) body.remove();
      showRichError(wrap, `Diagramm-Fehler:\n${err?.message || err}`);
    };
    ensureMermaidLoaded().then(() => {
      if (!wrap.isConnected) return;
      window.mermaid.initialize({
        startOnLoad: false,
        securityLevel: 'strict',
        theme: document.documentElement.dataset.theme === 'dark' ? 'dark' : 'default',
      });
      return window.mermaid.run({ nodes: [diagram] });
    }).catch(fail);
  };

  function normalizeChartConfig(input) {
    const cfg = { ...input };
    if (!cfg.type) cfg.type = 'bar';
    if (!cfg.data) {
      cfg.data = {
        labels: Array.isArray(cfg.labels) ? cfg.labels : [],
        datasets: Array.isArray(cfg.datasets) ? cfg.datasets : [],
      };
    }
    cfg.data.labels = Array.isArray(cfg.data.labels) ? cfg.data.labels : [];
    cfg.data.datasets = Array.isArray(cfg.data.datasets) ? cfg.data.datasets : [];

    const palette = ['#5357ff', '#17a673', '#e05252', '#d99b18', '#06b6d4', '#7c3aed'];
    cfg.data.datasets = cfg.data.datasets.map((dataset, index) => {
      const color = dataset.borderColor || dataset.backgroundColor || palette[index % palette.length];
      return {
        ...dataset,
        borderColor: dataset.borderColor || color,
        backgroundColor: dataset.backgroundColor || (cfg.type === 'line' ? `${color}33` : color),
        tension: dataset.tension ?? (cfg.type === 'line' ? 0.32 : undefined),
        fill: dataset.fill ?? false,
      };
    });

    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text').trim() || '#20232b';
    const gridColor = getComputedStyle(document.documentElement).getPropertyValue('--border').trim() || 'rgba(30,34,50,.12)';
    const userOptions = cfg.options || {};
    cfg.options = {
      ...userOptions,
      responsive: true,
      maintainAspectRatio: false,
      devicePixelRatio: Math.min(window.devicePixelRatio || 1, 2),
      resizeDelay: 80,
      interaction: { mode: 'index', intersect: false, ...(userOptions.interaction || {}) },
      plugins: {
        legend: { labels: { color: textColor, usePointStyle: true } },
        title: { display: !!cfg.title, text: cfg.title || '', color: textColor },
        ...(userOptions.plugins || {}),
      },
      scales: cfg.type === 'doughnut' || cfg.type === 'pie'
        ? userOptions.scales
        : {
            x: { ticks: { color: textColor }, grid: { color: gridColor } },
            y: { ticks: { color: textColor }, grid: { color: gridColor } },
            ...(userOptions.scales || {}),
          },
    };
    return cfg;
  }

  Leon.renderChartBlock = function renderChartBlock(code) {
    const pre = code.parentElement;
    if (!pre?.parentNode) return;
    let config;
    try {
      config = normalizeChartConfig(parseChartCandidate(code.innerText) || JSON.parse(code.innerText));
    } catch (err) {
      const wrap = richBlock('Chart');
      pre.parentNode.replaceChild(wrap, pre);
      showRichError(wrap, `Chart-Fehler:\n${err?.message || err}`);
      return;
    }
    const wrap = richBlock('Chart');
    const body = document.createElement('div');
    body.className = 'rich-chart-body';
    const canvas = document.createElement('canvas');
    body.appendChild(canvas);
    wrap.appendChild(body);
    pre.parentNode.replaceChild(wrap, pre);

    ensureChartLoaded().then(() => {
      if (!canvas.isConnected) return;
      const chart = new window.Chart(canvas, config);
      state.richCharts = state.richCharts || [];
      state.richCharts.push(chart);
    }).catch((err) => {
      if (body.isConnected) body.remove();
      showRichError(wrap, `Chart-Fehler:\n${err?.message || err}`);
    });
  };

  Leon.enhanceCodeBlocks = function enhanceCodeBlocks(root) {
    root.querySelectorAll('pre > code').forEach((code) => {
      if (code.closest('.code-wrap')) return;
      const lang = codeBlockLang(code) || 'txt';
      if (isMermaidLang(lang) || isChartLang(lang, code.innerText)) return;
      if (window.hljs) { try { hljs.highlightElement(code); } catch {} }
      const pre = code.parentElement;
      const wrap = document.createElement('div');
      wrap.className = 'code-wrap';
      const header = document.createElement('div');
      header.className = 'code-head';
      header.innerHTML = `<span class="code-lang">${esc(lang)}</span><div class="code-actions"><button class="code-btn" type="button">Kopieren</button><button class="code-btn" type="button">Als Datei</button></div>`;
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(header);
      wrap.appendChild(pre);
      const [copyBtn, fileBtn] = header.querySelectorAll('button');
      copyBtn.onclick = () => { navigator.clipboard.writeText(code.innerText); Leon.toast('Code kopiert.'); };
      fileBtn.onclick = () => Leon.downloadCode(code.innerText, lang);
    });
  };

  Leon.extForLang = function extForLang(lang) {
    const map = {
      python: 'py', py: 'py', javascript: 'js', js: 'js', typescript: 'ts', ts: 'ts',
      html: 'html', css: 'css', json: 'json', bash: 'sh', shell: 'sh', sh: 'sh',
      markdown: 'md', md: 'md', java: 'java', c: 'c', cpp: 'cpp', csharp: 'cs',
      php: 'php', ruby: 'rb', go: 'go', rust: 'rs', sql: 'sql', txt: 'txt',
    };
    return map[lang] || 'txt';
  };

  Leon.downloadCode = function downloadCode(code, lang) {
    const blob = new Blob([code], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `leon_code_${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.${Leon.extForLang(lang)}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  };

  function copyMessage(id) {
    const msg = state.messages.find(m => m.id === id);
    if (!msg) return;
    navigator.clipboard.writeText(msg.content || '');
    Leon.toast('Nachricht kopiert.');
  }

  async function toggleFavorite(id) {
    await api(`/api/messages/${id}/favorite`, { method: 'POST', body: '{}' });
    await Leon.loadMessages(true);
  }

  Leon.appendTempMessage = function appendTempMessage(role, content, extra = {}) {
    const temp = {
      id: 0,
      _tempId: 'tmp_' + (++state.tempSeq),
      parent_id: extra.parent_id ?? (state.activeLeafId ?? null),
      role: role === 'user' ? 'user' : 'ai',
      content,
      created: new Date().toISOString(),
      ...extra,
    };
    state.messages.push(temp);
    Leon.renderMessages();
    Leon.scrollBottom();
    return temp;
  };

  Leon.updateTempMessage = function updateTempMessage(temp, content) {
    temp.content = content;
    const el = document.querySelector(`[data-temp-id="${temp._tempId}"] .msg-content`);
    if (!el) { Leon.renderMessages(); return; }
    el.innerHTML = temp.role === 'user' ? esc(content) : Leon.renderMarkdown(content || '');
    Leon.renderRichBlocks(el);
    Leon.enhanceCodeBlocks(el);
    Leon.sanitizeRelativeImages(el);
    Leon.renderArtifacts();
  };

  Leon.scrollBottom = function scrollBottom() {
    const box = $('chat-box');
    box.scrollTop = box.scrollHeight;
  };

  Leon.setStreamingUi = function setStreamingUi(on) {
    state.isStreaming = on;
    $('send-btn').disabled = on;
    $('stop-btn').classList.toggle('show', on);
  };

  async function consumeSSEStream(res, aiMsg, onToken) {
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let full = '';
    let final = null;
    let lastPaint = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';
      let streamDone = false;
      for (const part of parts) {
        const line = part.split('\n').find(l => l.startsWith('data: '));
        if (!line) continue;
        const data = JSON.parse(line.slice(6));
        if (data.request_id) state.lastRequestId = data.request_id;
        if (data.error && !data.token) {
          const errText = data.error === true ? 'Stream-Fehler' : String(data.error);
          full += `\n⚠️ ${data.request_id ? `${errText} · ID ${data.request_id}` : errText}`;
        }
        if (data.token) {
          full += data.token;
          const now = performance.now();
          if (now - lastPaint > 70 || data.token.includes('\n')) {
            onToken(aiMsg, full);
            lastPaint = now;
            Leon.scrollBottom();
          }
        }
        if (data.done) { final = data; streamDone = true; break; }
      }
      if (streamDone) break;
    }
    return { full, final };
  }

  function openFilePicker() { $('file-input').click(); }

  function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ''));
      reader.onerror = () => reject(reader.error || new Error('Datei konnte nicht gelesen werden.'));
      reader.readAsDataURL(file);
    });
  }

  function readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ''));
      reader.onerror = () => reject(reader.error || new Error('Datei konnte nicht gelesen werden.'));
      reader.readAsText(file);
    });
  }

  async function handleFileUpload(file) {
    if (!file) return;
    if (state.isStreaming) { Leon.toast('Bitte warten, bis LEON fertig ist.'); return; }
    const name = String(file.name || '').toLowerCase();
    const ext = name.includes('.') ? name.split('.').pop() : '';
    const textExts = new Set(['txt', 'md', 'py', 'js', 'ts', 'html', 'htm', 'css', 'json', 'csv', 'log']);
    const blockedExts = new Set(['exe', 'dmg', 'pkg', 'app', 'zip', 'rar', '7z', 'tar', 'gz', 'pdf', 'doc', 'docx']);
    if (file.type && file.type.startsWith('image/')) {
      if (file.size > 8 * 1024 * 1024) { Leon.toast('Bild ist zu groß. Maximal 8 MB.'); return; }
      const dataUrl = await readFileAsDataURL(file);
      await sendImageMessage(file, dataUrl);
      return;
    }
    if (blockedExts.has(ext) || !textExts.has(ext)) {
      Leon.toast('Dieser Dateityp ist aus Sicherheitsgründen nicht für den Chat-Import freigegeben.');
      return;
    }
    if (file.size > 300 * 1024) { Leon.toast('Datei ist zu groß. Für Textdateien maximal ca. 300 KB.'); return; }
    const text = await readFileAsText(file);
    const current = $('user-input').value.trim();
    $('user-input').value = `${current ? current + '\n\n' : ''}--- Datei: ${file.name} ---\n${text}`.slice(0, 12000);
    Leon.autoResize($('user-input'));
    Leon.updateCharCount();
    $('user-input').focus();
    Leon.toast('Datei eingefügt. Du kannst jetzt senden.');
  }

  async function sendImageMessage(file, dataUrl) {
    if (!state.currentRoomId) return;
    const prompt = $('user-input').value.trim() || 'Beschreibe dieses Bild auf Deutsch.';
    const actualParentId = state.activeLeafId;
    $('user-input').value = '';
    Leon.autoResize($('user-input'));
    Leon.updateCharCount();
    Leon.appendTempMessage('user', `📎 Bild hochgeladen: ${file.name}\n${prompt}`, { parent_id: actualParentId, image_b64: dataUrl });
    const aiMsg = Leon.appendTempMessage('ai', thinkingHtml());
    state.isStreaming = true;
    Leon.setStreamingUi(true);
    state.aborter = new AbortController();
    let full = '';
    try {
      const res = await fetch('/chat/vision/stream', {
        method: 'POST',
        credentials: 'same-origin',
        signal: state.aborter.signal,
        headers: Leon.requestHeaders({ method: 'POST' }),
        body: JSON.stringify({
          room_id: state.currentRoomId,
          prompt,
          image_data_url: dataUrl,
          image_name: file.name,
          parent_id: actualParentId,
        }),
      });
      if (res.status === 401) { location.href = '/login'; return; }
      if (!res.ok) {
        throw await Leon.errorFromResponse(res, 'Bildanalyse fehlgeschlagen');
      }
      const result = await consumeSSEStream(res, aiMsg, Leon.updateTempMessage);
      full = result.full;
      if (result.final?.msg_id) state.activeLeafId = result.final.msg_id;
      else if (result.final?.user_msg_id) state.activeLeafId = result.final.user_msg_id;
      Leon.updateTempMessage(aiMsg, full || '');
      Leon.scrollBottom();
    } catch (e) {
      if (e.name !== 'AbortError') {
        const label = Leon.errorLabel(e, 'Bildanalyse fehlgeschlagen');
        Leon.updateTempMessage(aiMsg, `⚠️ ${label}`);
        Leon.toast(label);
      }
    } finally {
      state.isStreaming = false;
      state.aborter = null;
      Leon.setStreamingUi(false);
      await Leon.loadRooms();
      await Leon.loadMessages(true);
      setTimeout(() => Leon.loadRooms().catch(() => {}), 1200);
      Leon.scrollBottom();
    }
  }

  async function sendMessage(overrideMsg = null, parentId = undefined) {
    const input = $('user-input');
    const msg = overrideMsg || input.value.trim();
    if (!msg || state.isStreaming || !state.currentRoomId) return;
    if (!overrideMsg) input.value = '';
    Leon.autoResize(input);
    Leon.updateCharCount();
    
    // Resolve parent_id: undefined means "continue current branch"; null is a real root branch.
    const actualParentId = parentId !== undefined
      ? parentId
      : (state.editParentId !== undefined ? state.editParentId : state.activeLeafId);
    if (parentId !== undefined) state.activeLeafId = actualParentId;
    state.editParentId = undefined;
    
    const userTemp = Leon.appendTempMessage('user', msg, { parent_id: actualParentId });
    const aiTemp = Leon.appendTempMessage('ai', thinkingHtml(), { parent_id: 0 }); // ai parent will be user_msg_id
    
    state.isStreaming = true;
    Leon.setStreamingUi(true);
    state.aborter = new AbortController();
    let full = '';
    try {
      const res = await fetch('/chat/stream', {
        method: 'POST',
        credentials: 'same-origin',
        signal: state.aborter.signal,
        headers: Leon.requestHeaders({ method: 'POST' }),
        body: JSON.stringify({ room_id: state.currentRoomId, message: msg, parent_id: actualParentId }),
      });
      if (res.status === 401) { location.href = '/login'; return; }
      if (!res.ok) {
        throw await Leon.errorFromResponse(res, 'Antwort fehlgeschlagen');
      }
      const result = await consumeSSEStream(res, aiTemp, Leon.updateTempMessage);
      full = result.full;
      if (result.final?.msg_id) state.activeLeafId = result.final.msg_id;
      else if (result.final?.user_msg_id) state.activeLeafId = result.final.user_msg_id;
      Leon.updateTempMessage(aiTemp, full || '');
      Leon.scrollBottom();
    } catch (e) {
      if (e.name !== 'AbortError') {
        const label = Leon.errorLabel(e, 'Antwort fehlgeschlagen');
        Leon.updateTempMessage(aiTemp, `⚠️ ${label}`);
        Leon.toast(label);
      }
    } finally {
      state.isStreaming = false;
      state.aborter = null;
      Leon.setStreamingUi(false);
      await Leon.loadRooms();
      await Leon.loadMessages(true);
      setTimeout(() => Leon.loadRooms().catch(() => {}), 1200);
      Leon.scrollBottom();
    }
  }

  function stopGeneration() {
    if (state.aborter) state.aborter.abort();
    Leon.setStreamingUi(false);
    Leon.toast('Antwort gestoppt.');
  }

  async function clearOldBrowserCache() {
    try {
      if ('serviceWorker' in navigator) {
        const regs = await navigator.serviceWorker.getRegistrations();
        regs.forEach(r => r.unregister());
      }
      if (window.caches) {
        const keys = await caches.keys();
        await Promise.all(keys.map(k => caches.delete(k)));
      }
    } catch {}
  }

  async function init() {
    await clearOldBrowserCache();
    Leon.resetArtifactPanel?.();
    Leon.applyTheme(localStorage.getItem('leon-theme') || 'light');
    Leon.setFontSize(localStorage.getItem('leon-font-size') || 'md');
    Leon.applyTopActionsCollapsed(localStorage.getItem('leon-tools-collapsed') === '1');
    Leon.applySidebarCollapsed(localStorage.getItem('leon-sidebar-collapsed') === '1');
    Leon.updateAvatarUi();
    await Leon.checkStatus();
    await Leon.loadRooms();
    await Leon.loadMessages();
    Leon.routeFromUrl();
  }

  $('file-input').addEventListener('change', async (e) => {
    const file = e.target.files && e.target.files[0];
    e.target.value = '';
    try { await handleFileUpload(file); } catch (err) { Leon.toast(err.message || 'Upload fehlgeschlagen.'); }
  });

  $('user-input').addEventListener('input', (e) => {
    Leon.autoResize(e.target);
    Leon.updateCharCount();
  });

  $('user-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  Object.assign(window, {
    copyMessage,
    toggleFavorite,
    openFilePicker,
    sendMessage,
    stopGeneration,
  });

  init().catch(e => {
    console.error(e);
    Leon.toast('Start fehlgeschlagen: ' + e.message);
  });
})();
