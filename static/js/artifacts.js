/** LEON AI – Live artifact preview panel */
(function () {
  const { state, $ } = Leon;

  const escapeScriptEnd = (code) => String(code || '').replace(/<\/script/gi, '<\\/script');
  const escapeStyleEnd = (code) => String(code || '').replace(/<\/style/gi, '<\\/style');
  const escapeHtml = (text) => String(text || '').replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;',
  }[m]));

  function stableHash(text) {
    let hash = 2166136261;
    const input = String(text || '');
    for (let i = 0; i < input.length; i++) {
      hash ^= input.charCodeAt(i);
      hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
    }
    return (hash >>> 0).toString(36);
  }

  function safeRelativeAssets(html) {
    let out = String(html || '');
    let blocked = 0;
    out = out.replace(/<head(\s[^>]*)?>/i, match => `${match}<base href="about:blank">`);
    if (!/<base\s/i.test(out)) {
      out = out.replace(/<html(\s[^>]*)?>/i, match => `${match}<head><base href="about:blank"></head>`);
    }
    out = out.replace(
      /\s(src|href)=["'](?!https?:|data:|blob:|mailto:|tel:|#|about:|\/static\/)([^"']+)["']/gi,
      (_match, attr, url) => {
        blocked += 1;
        const clean = String(url || '').trim();
        if (attr.toLowerCase() === 'src') {
          return ` data-leon-${attr}="${escapeHtml(clean)}"`;
        }
        return ` ${attr}="about:blank" data-leon-${attr}="${escapeHtml(clean)}"`;
      },
    );
    if (blocked > 0) {
      out = out.replace(/<body(\s[^>]*)?>/i, match => `${match}<meta name="leon-neutralized-assets" content="${blocked}">`);
    }
    return out;
  }

  function injectTailwind(html) {
    let out = String(html || '');
    if (/cdn\.tailwindcss\.com/i.test(out)) return out;
    const script = '<script src="https://cdn.tailwindcss.com"><\\/script>';
    if (/<\/head>/i.test(out)) return out.replace(/<\/head>/i, `${script}</head>`);
    if (/<html[\s>]/i.test(out)) return out.replace(/<html(\s[^>]*)?>/i, match => `${match}<head>${script}</head>`);
    return `${script}${out}`;
  }

  function artifactBridgeBody() {
    return `
(() => {
  const isNoise = (message) =>
    /cdn\\.tailwindcss\\.com should not be used in production/i.test(message) ||
    /^Script error\\.?$/i.test(String(message || "").trim()) ||
    /ResizeObserver loop/i.test(message);
  const safe = (value) => {
    try {
      if (value instanceof Error) return value.stack || value.message;
      if (typeof value === "object") return JSON.stringify(value);
      return String(value);
    } catch (_) { return String(value); }
  };
  const send = (level, args) => {
    try {
      const message = Array.from(args).map(safe).join(" ");
      if (isNoise(message)) return true;
      parent.postMessage({ type: "leon-artifact-log", level, message }, "*");
    } catch (_) {}
    return false;
  };
  ["log", "info", "warn", "error"].forEach((level) => {
    const original = console[level] || console.log;
    console[level] = (...args) => {
      const ignored = send(level, args);
      if (ignored) return undefined;
      return original.apply(console, args);
    };
  });
  window.addEventListener("load", () => {
    send("system", ["Vorschau geladen."]);
  });
  window.addEventListener("error", (event) => {
    const msg = event.message || "Unbekannter Fehler";
    if (/^Script error\\.?$/i.test(String(msg).trim()) && !event.error) return;
    send("error", [msg, event.filename ? event.filename + ":" + event.lineno : ""]);
  });
  window.addEventListener("unhandledrejection", (event) => {
    send("error", ["Unhandled Promise", event.reason && (event.reason.stack || event.reason.message || event.reason)]);
  });
})();
`;
  }

  function artifactBridgeScript() {
    return `<script>${artifactBridgeBody()}<\/script>`;
  }

  function injectArtifactBridge(html) {
    let out = String(html || '');
    if (out.includes('leon-artifact-log')) return out;
    const script = artifactBridgeScript();
    if (/<\/head>/i.test(out)) return out.replace(/<\/head>/i, `${script}</head>`);
    if (/<html[\s>]/i.test(out)) return out.replace(/<html(\s[^>]*)?>/i, match => `${match}<head>${script}</head>`);
    return `${script}${out}`;
  }

  Leon.extractRunnableArtifacts = function extractRunnableArtifacts() {
    const artifacts = [];
    const sourceMessages = typeof Leon.getActivePath === 'function'
      ? Leon.getActivePath()
      : (state.messages || []);
    for (const msg of sourceMessages) {
      if (msg.role !== 'ai' || !msg.content) continue;
      const text = String(msg.content);
      const blocks = [];
      const re = /```([A-Za-z0-9_+#.-]*)\n([\s\S]*?)```/g;
      let match;
      while ((match = re.exec(text)) !== null) {
        blocks.push({ lang: (match[1] || '').trim().toLowerCase(), code: match[2] || '' });
      }
      if (!blocks.length && /<html[\s>]|<!doctype html|<script[\s>]|<style[\s>]/i.test(text)) {
        blocks.push({ lang: 'html', code: text });
      }
      if (!blocks.length) continue;
      const htmlBlocks = blocks.filter(b =>
        ['html', 'htm'].includes(b.lang) || /<html[\s>]|<!doctype html|<body[\s>]/i.test(b.code)
      );
      const cssBlocks = blocks.filter(b => ['css', 'style'].includes(b.lang));
      const jsBlocks = blocks.filter(b => ['js', 'javascript', 'ts', 'typescript'].includes(b.lang));
      const pyBlocks = blocks.filter(b => ['py', 'python'].includes(b.lang));

      if (htmlBlocks.length || cssBlocks.length || jsBlocks.length || pyBlocks.length) {
        if (pyBlocks.length) {
          const pyCode = pyBlocks.map(b => b.code).join('\n\n');
          artifacts.push({
            title: 'Python-Vorschau',
            lang: 'Python (Pyodide)',
            html: Leon.buildPyodideHtml(pyCode),
            source: blocks.map(b => '```' + (b.lang || '') + '\n' + b.code + '\n```').join('\n\n'),
            message_id: msg.id || null,
          });
        } else {
          const base = htmlBlocks.length ? htmlBlocks[htmlBlocks.length - 1].code : '<div id="app">Vorschau bereit.</div>';
          const css = cssBlocks.map(b => b.code).join('\n\n');
          const js = jsBlocks.map(b => b.code).join('\n\n');
          artifacts.push({
            title: htmlBlocks.length ? 'HTML-Vorschau' : 'JS/CSS-Vorschau',
            lang: [htmlBlocks.length && 'HTML', css && 'CSS', js && 'JS'].filter(Boolean).join(' + '),
            html: Leon.buildPreviewHtml(base, css, js),
            source: blocks.map(b => '```' + (b.lang || '') + '\n' + b.code + '\n```').join('\n\n'),
            message_id: msg.id || null,
          });
        }
      }
    }
    return artifacts;
  };

  function normalizePersistedArtifact(version, index) {
    if (version?.persisted && version.key) {
      return {
        ...version,
        label: version.label || `${index + 1}. ${version.title || version.lang || 'Artifact'} · gespeichert`,
      };
    }
    return {
      id: version.id,
      persisted: true,
      title: version.title || `Artifact ${index + 1}`,
      lang: version.language || version.lang || 'HTML / CSS / JS',
      html: version.html || '',
      source: version.source || '',
      message_id: version.message_id || null,
      content_hash: version.content_hash || '',
      key: version.artifact_key || version.content_hash || `persisted:${version.id}`,
      label: `${index + 1}. ${version.title || version.language || 'Artifact'} · gespeichert`,
      created: version.created || '',
    };
  }

  Leon.loadArtifactHistory = async function loadArtifactHistory(roomId) {
    if (!roomId) {
      state.artifactHistory = [];
      state.artifactHistoryRoomId = null;
      return;
    }
    if (state.artifactHistoryRoomId === roomId) return;
    try {
      const data = await Leon.api(`/api/rooms/${roomId}/artifacts`);
      state.artifactHistory = (data?.versions || []).map(normalizePersistedArtifact);
      state.artifactHistoryRoomId = roomId;
      state.artifactSyncedKeys = new Set(state.artifactHistory.map(a => a.key));
    } catch (err) {
      state.artifactHistory = [];
      state.artifactHistoryRoomId = roomId;
      Leon.reportClientError?.('artifact-history', err.message || err, 'artifact-history');
    }
  };

  Leon.syncArtifactHistory = async function syncArtifactHistory(extracted) {
    if (!state.currentRoomId || state.artifactSyncing) return;
    const savedKeys = state.artifactSyncedKeys || new Set((state.artifactHistory || []).map(a => a.key));
    state.artifactSyncedKeys = savedKeys;
    const unsaved = (extracted || []).filter(artifact =>
      artifact.message_id && artifact.html && !savedKeys.has(artifact.key)
    );
    if (!unsaved.length) return;
    unsaved.forEach(artifact => savedKeys.add(artifact.key));
    state.artifactSyncing = true;
    try {
      const result = await Leon.api(`/api/rooms/${state.currentRoomId}/artifacts`, {
        method: 'POST',
        body: JSON.stringify({ artifacts: unsaved.map(artifact => ({
          key: artifact.key,
          title: artifact.title,
          lang: artifact.lang,
          html: artifact.html,
          source: artifact.source,
          message_id: artifact.message_id,
        })) }),
      });
      state.artifactHistory = (result?.versions || []).map(normalizePersistedArtifact);
      state.artifactHistoryRoomId = state.currentRoomId;
      state.artifactSyncedKeys = new Set(state.artifactHistory.map(a => a.key));
    } catch (err) {
      unsaved.forEach(artifact => savedKeys.delete(artifact.key));
      Leon.reportClientError?.('artifact-sync', err.message || err, 'artifact-sync');
    } finally {
      state.artifactSyncing = false;
      Leon.updateArtifactSelect();
    }
  };

  Leon.buildPyodideHtml = function buildPyodideHtml(pyCode) {
    const safeCode = escapeScriptEnd(pyCode).replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');
    return `<!doctype html><html><head><meta charset="utf-8">
<base href="about:blank">
<script src="https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js"><\/script>
<style>
body{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#15171d;color:#e5e7eb;margin:0;padding:16px;white-space:pre-wrap;line-height:1.55}
.status{color:#9ca3af}.ok{color:#86efac}.err{color:#fca5a5}
</style>
</head><body>
<div id="out"><span class="status">Lädt Python-Umgebung (Pyodide)...</span></div>
<script>
${artifactBridgeBody()}
  function write(msg, cls) {
    const out = document.getElementById("out");
    if (cls) out.innerHTML += '<span class="' + cls + '">' + String(msg).replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m])) + '</span>';
    else out.innerText += msg;
  }
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = resolve;
      s.onerror = () => reject(new Error("Pyodide konnte nicht geladen werden. Prüfe Internet/CDN oder lokale Einbindung."));
      document.head.appendChild(s);
    });
  }
  function waitForLoadPyodide(timeout = 10000) {
    const started = Date.now();
    return new Promise((resolve, reject) => {
      const tick = () => {
        if (typeof globalThis.loadPyodide === "function") return resolve(globalThis.loadPyodide);
        if (Date.now() - started > timeout) return reject(new Error("loadPyodide ist nicht verfügbar. Pyodide-Skript wurde nicht korrekt geladen."));
        setTimeout(tick, 80);
      };
      tick();
    });
  }
  async function ensurePyodideLoader() {
    if (typeof globalThis.loadPyodide === "function") return globalThis.loadPyodide;
    try {
      return await waitForLoadPyodide(4000);
    } catch (_) {}
    await loadScript("https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js");
    return waitForLoadPyodide();
  }
  async function run() {
    try {
      const loadPyodideFn = await ensurePyodideLoader();
      const pyodide = await loadPyodideFn({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/" });
      document.getElementById("out").innerText = "Führe Skript aus...\\n\\n";
      pyodide.setStdout({ batched: (msg) => { document.getElementById("out").innerText += msg + "\\n"; } });
      pyodide.setStderr({ batched: (msg) => { document.getElementById("out").innerText += "Fehler: " + msg + "\\n"; } });
      await pyodide.runPythonAsync(\`${safeCode}\`);
      document.getElementById("out").innerText += "\\n[Beendet]";
    } catch (err) {
      document.getElementById("out").innerText += "\\nFehler:\\n" + err;
    }
  }
  run();
</script>
</body></html>`;
  };

  Leon.buildPreviewHtml = function buildPreviewHtml(base, css, js) {
    let html = String(base || '');
    if (!/<html[\s>]/i.test(html)) {
      html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{font-family:system-ui,-apple-system,BlinkMacSystemFont,sans-serif;margin:24px;background:#fff;color:#111}</style></head><body>${html}</body></html>`;
    }
    html = injectArtifactBridge(html);
    html = injectTailwind(html);
    if (css) {
      const style = `<style>\n${escapeStyleEnd(css)}\n</style>`;
      html = /<\/head>/i.test(html) ? html.replace(/<\/head>/i, style + '</head>') : style + html;
    }
    if (js) {
      const script = `<script>\ntry{\n${escapeScriptEnd(js)}\n}catch(e){document.body.insertAdjacentHTML('beforeend','<pre style="color:#b91c1c;background:#fee2e2;padding:12px;border-radius:10px;white-space:pre-wrap">'+String(e).replace(/[&<>]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]))+'</pre>')}\n<\/script>`;
      html = /<\/body>/i.test(html) ? html.replace(/<\/body>/i, script + '</body>') : html + script;
    }
    return safeRelativeAssets(html);
  };

  Leon.renderArtifacts = function renderArtifacts() {
    const panel = $('artifact-panel');
    const frame = $('artifact-frame');
    const empty = $('artifact-empty');
    const meta = $('artifact-meta');
    if (!panel || !frame) return;

    const extractedArtifacts = Leon.extractRunnableArtifacts().map((artifact, index) => ({
      ...artifact,
      key: artifact.lang + ':' + stableHash(`${artifact.html}\n---source---\n${artifact.source}`),
      label: `${index + 1}. ${artifact.title || artifact.lang || 'Artifact'} · aktuell`,
    }));
    Leon.syncArtifactHistory(extractedArtifacts);
    const history = (state.artifactHistory || []).map(normalizePersistedArtifact);
    const historyKeys = new Set(history.map(artifact => artifact.key));
    const artifacts = [
      ...history,
      ...extractedArtifacts.filter(artifact => !historyKeys.has(artifact.key)),
    ].map((artifact, index) => ({
      ...artifact,
      label: artifact.label || `${index + 1}. ${artifact.title || artifact.lang || 'Artifact'}`,
    }));
    if (!artifacts.length) {
      panel.classList.remove('show', 'fullscreen');
      $('main')?.classList.remove('artifacts-open');
      state.activeArtifact = null;
      state.artifacts = [];
      state.artifactIndex = -1;
      state.artifactCount = 0;
      state.artifactKey = '';
      Leon.updateArtifactSelect();
      Leon.updateArtifactReopen(false);
      return;
    }

    state.artifacts = artifacts;
    if (state.artifactCount !== artifacts.length) {
      state.artifactIndex = artifacts.length - 1;
      state.artifactCount = artifacts.length;
    } else if (state.artifactIndex < 0 || state.artifactIndex >= artifacts.length) {
      const currentIdx = artifacts.findIndex(item => item.key === state.artifactKey);
      state.artifactIndex = currentIdx >= 0 ? currentIdx : artifacts.length - 1;
    }
    const artifact = artifacts[state.artifactIndex] || artifacts[artifacts.length - 1];
    const key = artifact.key;
    state.activeArtifact = artifact;
    Leon.updateArtifactSelect();
    if (meta) {
      const bits = [artifact.lang || 'HTML / CSS / JS'];
      bits.push(artifact.persisted ? 'gespeichert' : 'aktuell');
      if (artifact.created) bits.push(new Date(artifact.created).toLocaleString('de-DE'));
      meta.textContent = bits.join(' · ');
    }
    if (empty) empty.style.display = 'none';
    if (state.artifactKey !== key) {
      state.artifactLogs = [];
      state.artifactErrors = [];
      frame.srcdoc = artifact.html;
      state.artifactKey = key;
      Leon.renderArtifactPanels();
    }
    Leon.updateArtifactCode();
    if (!state.isStreaming && state.artifactClosedKey !== key) {
      panel.classList.add('show');
      $('main')?.classList.add('artifacts-open');
      Leon.updateArtifactReopen(false);
    } else {
      Leon.updateArtifactReopen(state.artifactClosedKey === key);
    }
  };

  Leon.updateArtifactSelect = function updateArtifactSelect() {
    const select = $('artifact-select');
    if (!select) return;
    const artifacts = state.artifacts || [];
    select.style.display = artifacts.length > 1 ? '' : 'none';
    select.innerHTML = artifacts.map((artifact, index) =>
      `<option value="${index}">${escapeHtml(artifact.label || `Artifact ${index + 1}`)}</option>`
    ).join('');
    if (state.artifactIndex >= 0) select.value = String(state.artifactIndex);
    const deleteBtn = $('artifact-delete');
    if (deleteBtn) {
      deleteBtn.style.display = state.activeArtifact?.persisted ? '' : 'none';
      deleteBtn.disabled = !state.activeArtifact?.persisted;
    }
    const allBtn = $('artifact-download-all');
    if (allBtn) {
      allBtn.style.display = artifacts.length > 1 ? '' : 'none';
      allBtn.disabled = artifacts.length < 1;
    }
  };

  Leon.updateArtifactCode = function updateArtifactCode() {
    const code = $('artifact-code');
    if (!code) return;
    code.textContent = state.activeArtifact?.source || state.activeArtifact?.html || '';
  };

  Leon.renderArtifactPanels = function renderArtifactPanels() {
    Leon.updateArtifactCode();
    const consoleEl = $('artifact-console');
    const errorsEl = $('artifact-errors');
    const rowHtml = (items, empty) => items.length
      ? items.slice(-80).reverse().map(item => `<div class="artifact-log-row ${escapeHtml(item.level || '')}"><span class="artifact-log-level">${escapeHtml(item.level || 'log')}</span>${escapeHtml(item.message || '')}</div>`).join('')
      : `<div class="artifact-empty">${empty}</div>`;
    if (consoleEl) consoleEl.innerHTML = rowHtml(state.artifactLogs || [], 'Noch keine Terminalmeldungen.');
    if (errorsEl) errorsEl.innerHTML = rowHtml(state.artifactErrors || [], 'Noch keine Fehler.');
  };

  function switchArtifactTab(tab = 'preview') {
    state.artifactTab = tab;
    document.querySelectorAll('[data-artifact-tab]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.artifactTab === tab);
    });
    document.querySelectorAll('[data-artifact-view]').forEach(view => {
      view.classList.toggle('active', view.dataset.artifactView === tab);
    });
    Leon.renderArtifactPanels();
  }

  function appendArtifactLog(level, message) {
    const text = String(message || '').trim();
    if (!text || /cdn\.tailwindcss\.com should not be used in production/i.test(text)) return;
    if (/^Script error\.?$/i.test(text) || /ResizeObserver loop/i.test(text)) return;
    const cleanLevel = ['error', 'warn', 'info', 'log', 'system'].includes(level) ? level : 'log';
    const item = {
      level: cleanLevel,
      message: `[${new Date().toLocaleTimeString('de-DE')}] ${text.slice(0, 1200)}`,
    };
    state.artifactLogs.push(item);
    if (cleanLevel === 'error') {
      state.artifactErrors.push(item);
      Leon.reportClientError?.('artifact-error', item.message, 'artifact-preview');
    }
    Leon.renderArtifactPanels();
  }

  window.addEventListener('message', (event) => {
    const frame = $('artifact-frame');
    if (!frame || event.source !== frame.contentWindow) return;
    const data = event.data || {};
    if (data.type !== 'leon-artifact-log') return;
    appendArtifactLog(data.level, data.message);
  });

  Leon.updateArtifactReopen = function updateArtifactReopen(show = false) {
    const btn = $('artifact-reopen');
    if (!btn) return;
    btn.classList.toggle('show', !!show && !!state.activeArtifact);
  };

  function copyArtifactCode() {
    if (!state.activeArtifact) return;
    navigator.clipboard.writeText(state.activeArtifact.source || state.activeArtifact.html || '');
    Leon.toast('Vorschau-Code kopiert.');
  }

  function downloadBlob(filename, type, content) {
    const blob = content instanceof Blob ? content : new Blob([content], { type });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(a.href);
  }

  function artifactFilename(ext) {
    const label = (state.activeArtifact?.title || state.activeArtifact?.lang || 'artifact')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '') || 'artifact';
    return `leon-${label}-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.${ext}`;
  }

  function downloadArtifactHtml() {
    if (!state.activeArtifact) return;
    downloadBlob(artifactFilename('html'), 'text/html;charset=utf-8', state.activeArtifact.html || '');
    Leon.toast('HTML heruntergeladen.');
  }

  function crc32Table() {
    if (Leon._crc32Table) return Leon._crc32Table;
    Leon._crc32Table = Array.from({ length: 256 }, (_v, n) => {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      return c >>> 0;
    });
    return Leon._crc32Table;
  }

  function crc32(bytes) {
    let crc = 0xffffffff;
    const table = crc32Table();
    for (const byte of bytes) crc = table[(crc ^ byte) & 0xff] ^ (crc >>> 8);
    return (crc ^ 0xffffffff) >>> 0;
  }

  function u16(n) { return [n & 0xff, (n >>> 8) & 0xff]; }
  function u32(n) { return [n & 0xff, (n >>> 8) & 0xff, (n >>> 16) & 0xff, (n >>> 24) & 0xff]; }

  function zipBlob(files) {
    const encoder = new TextEncoder();
    const chunks = [];
    const central = [];
    let offset = 0;
    files.forEach((file) => {
      const name = encoder.encode(file.name);
      const data = encoder.encode(file.content || '');
      const crc = crc32(data);
      const local = new Uint8Array([
        ...u32(0x04034b50), ...u16(20), ...u16(0), ...u16(0), ...u16(0), ...u16(0),
        ...u32(crc), ...u32(data.length), ...u32(data.length), ...u16(name.length), ...u16(0),
      ]);
      chunks.push(local, name, data);
      central.push({
        name,
        crc,
        size: data.length,
        offset,
      });
      offset += local.length + name.length + data.length;
    });
    const centralStart = offset;
    central.forEach((file) => {
      const header = new Uint8Array([
        ...u32(0x02014b50), ...u16(20), ...u16(20), ...u16(0), ...u16(0), ...u16(0), ...u16(0),
        ...u32(file.crc), ...u32(file.size), ...u32(file.size), ...u16(file.name.length), ...u16(0), ...u16(0),
        ...u16(0), ...u16(0), ...u32(0), ...u32(file.offset),
      ]);
      chunks.push(header, file.name);
      offset += header.length + file.name.length;
    });
    const centralSize = offset - centralStart;
    chunks.push(new Uint8Array([
      ...u32(0x06054b50), ...u16(0), ...u16(0), ...u16(central.length), ...u16(central.length),
      ...u32(centralSize), ...u32(centralStart), ...u16(0),
    ]));
    return new Blob(chunks, { type: 'application/zip' });
  }

  function downloadArtifactZip() {
    if (!state.activeArtifact) return;
    const files = [
      { name: 'preview.html', content: state.activeArtifact.html || '' },
      { name: 'source.md', content: state.activeArtifact.source || '' },
      { name: 'console.txt', content: (state.artifactLogs || []).map(item => item.message).join('\n') },
      { name: 'errors.txt', content: (state.artifactErrors || []).map(item => item.message).join('\n') },
    ];
    downloadBlob(artifactFilename('zip'), 'application/zip', zipBlob(files));
    Leon.toast('ZIP heruntergeladen.');
  }

  function safeZipName(value, fallback) {
    return (String(value || fallback || 'artifact')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '') || 'artifact').slice(0, 42);
  }

  function downloadAllArtifactsZip() {
    const artifacts = state.artifacts || [];
    if (!artifacts.length) return;
    const files = [];
    artifacts.forEach((artifact, index) => {
      const prefix = `${String(index + 1).padStart(2, '0')}-${safeZipName(artifact.title || artifact.lang, 'artifact')}`;
      files.push({ name: `${prefix}/preview.html`, content: artifact.html || '' });
      files.push({ name: `${prefix}/source.md`, content: artifact.source || '' });
      files.push({
        name: `${prefix}/meta.json`,
        content: JSON.stringify({
          id: artifact.id || null,
          title: artifact.title || '',
          language: artifact.lang || '',
          message_id: artifact.message_id || null,
          persisted: !!artifact.persisted,
          created: artifact.created || '',
        }, null, 2),
      });
    });
    downloadBlob(`leon-artifacts-${new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')}.zip`, 'application/zip', zipBlob(files));
    Leon.toast('Alle Artifact-Versionen als ZIP heruntergeladen.');
  }

  async function deleteArtifactVersion() {
    const artifact = state.activeArtifact;
    if (!artifact?.persisted || !artifact.id || !state.currentRoomId) return;
    if (!confirm(`Gespeicherte Version "${artifact.title || 'Artifact'}" löschen?`)) return;
    try {
      const result = await Leon.api(`/api/rooms/${state.currentRoomId}/artifacts/${artifact.id}`, {
        method: 'DELETE',
      });
      state.artifactHistory = (result?.versions || []).map(normalizePersistedArtifact);
      state.artifactHistoryRoomId = state.currentRoomId;
      state.artifactSyncedKeys = new Set(state.artifactHistory.map(a => a.key));
      state.artifactIndex = Math.max(0, Math.min(state.artifactIndex, (state.artifacts || []).length - 2));
      state.artifactKey = '';
      Leon.renderArtifacts();
      Leon.toast('Artifact-Version gelöscht.');
    } catch (err) {
      Leon.toast(Leon.errorLabel ? Leon.errorLabel(err, 'Löschen fehlgeschlagen.') : (err.message || 'Löschen fehlgeschlagen.'));
    }
  }

  function switchArtifactVersion(value) {
    const index = Number(value);
    if (!Number.isInteger(index) || index < 0 || index >= (state.artifacts || []).length) return;
    state.artifactIndex = index;
    state.artifactKey = '';
    Leon.renderArtifacts();
    switchArtifactTab(state.artifactTab || 'preview');
  }

  function openArtifactsPanel() {
    const panel = $('artifact-panel');
    if (!panel || !state.activeArtifact) return;
    state.artifactClosedKey = '';
    panel.classList.add('show');
    $('main')?.classList.add('artifacts-open');
    Leon.updateArtifactReopen(false);
  }

  function refreshArtifactPreview() {
    const frame = $('artifact-frame');
    if (!frame || !state.activeArtifact) return;
    state.artifactLogs = [];
    state.artifactErrors = [];
    state.artifactKey = '';
    frame.srcdoc = state.activeArtifact.html;
    appendArtifactLog('system', 'Vorschau wurde neu gestartet.');
    Leon.renderArtifactPanels();
    Leon.toast('Vorschau aktualisiert.');
  }

  function askLeonAboutArtifact() {
    const input = $('user-input');
    if (!input || !state.activeArtifact) return;
    input.value = `Bitte prüfe diesen Vorschau-Code auf Fehler und Verbesserungen:\\n\\n${state.activeArtifact.source || state.activeArtifact.html || ''}`.slice(0, 12000);
    Leon.autoResize?.(input);
    Leon.updateCharCount?.();
    input.focus();
    Leon.toast('Code liegt im Eingabefeld.');
  }

  function closeArtifactsPanel() {
    if (state.artifactKey) state.artifactClosedKey = state.artifactKey;
    const panel = $('artifact-panel');
    panel?.classList.remove('show', 'fullscreen');
    $('main')?.classList.remove('artifacts-open');
    Leon.updateArtifactReopen(!!state.activeArtifact);
  }

  function toggleArtifactFullscreen() {
    const panel = $('artifact-panel');
    const btn = $('artifact-fullscreen');
    if (!panel) return;
    const full = !panel.classList.contains('fullscreen');
    panel.classList.toggle('fullscreen', full);
    if (btn) btn.textContent = full ? 'Normal' : 'Vollbild';
  }

  Object.assign(window, {
    copyArtifactCode,
    downloadArtifactHtml,
    downloadArtifactZip,
    downloadAllArtifactsZip,
    deleteArtifactVersion,
    refreshArtifactPreview,
    askLeonAboutArtifact,
    switchArtifactTab,
    switchArtifactVersion,
    openArtifactsPanel,
    closeArtifactsPanel,
    toggleArtifactFullscreen,
  });
})();
