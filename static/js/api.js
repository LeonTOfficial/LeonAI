/** LEON AI – Shared state and API layer */
window.Leon = window.Leon || {};

Leon.state = {
  rooms: [],
  models: [],
  fastModels: [],
  currentRoomId: null,
  currentRoom: null,
  messages: [],
  activeLeafId: null,
  editParentId: undefined,
  isStreaming: false,
  aborter: null,
  lastStatus: null,
  lastRequestId: '',
  tempSeq: 0,
  artifactClosedKey: '',
  artifactKey: '',
  activeArtifact: null,
  artifacts: [],
  artifactHistory: [],
  artifactHistoryRoomId: null,
  artifactSyncing: false,
  artifactIndex: -1,
  artifactCount: 0,
  richCharts: [],
  artifactTab: 'preview',
  artifactLogs: [],
  artifactErrors: [],
};

Leon.$ = (id) => document.getElementById(id);

Leon.esc = (s) => String(s ?? '').replace(/[&<>"']/g, m => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;',
}[m]));

Leon.fmtTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? '' : d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
};

Leon.cleanModel = (m) => String(m || 'llama3').replace(/:latest$/, '');

Leon.csrfToken = function csrfToken() {
  return document.querySelector('meta[name="csrf-token"]')?.content || '';
};

Leon.requestHeaders = function requestHeaders(options = {}) {
  const method = String(options.method || 'GET').toUpperCase();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const token = Leon.csrfToken();
    if (token) headers['X-CSRF-Token'] = token;
  }
  return headers;
};

Leon.makeApiError = function makeApiError(message, detail = {}) {
  const err = new Error(message || 'Fehler');
  err.requestId = detail.requestId || '';
  err.status = detail.status || 0;
  err.payload = detail.payload || {};
  return err;
};

Leon.errorLabel = function errorLabel(err, fallback = 'Fehler') {
  const message = err?.message || fallback;
  return err?.requestId ? `${message} · ID ${err.requestId}` : message;
};

Leon.errorFromResponse = async function errorFromResponse(res, fallback = 'Fehler') {
  const requestId = res.headers.get('X-Request-ID') || '';
  if (requestId) Leon.state.lastRequestId = requestId;
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
  const message = data.error || data.message || fallback;
  return Leon.makeApiError(message, {
    requestId: data.request_id || requestId,
    status: res.status,
    payload: data,
  });
};

Leon.api = async function api(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    credentials: 'same-origin',
    headers: Leon.requestHeaders(options),
  });
  const requestId = res.headers.get('X-Request-ID') || '';
  if (requestId) Leon.state.lastRequestId = requestId;
  if (res.status === 401) { location.href = '/login'; return null; }
  const text = await res.text();
  let data = {};
  try { data = text ? JSON.parse(text) : {}; } catch { data = { raw: text }; }
  if (!res.ok) {
    throw Leon.makeApiError(data.error || data.message || 'Fehler', {
      requestId: data.request_id || requestId,
      status: res.status,
      payload: data,
    });
  }
  return data;
};

Leon.reportClientError = function reportClientError(kind, message, source = '', stack = '') {
  const payload = JSON.stringify({
    kind: String(kind || 'frontend').slice(0, 40),
    message: String(message || '').slice(0, 600),
    source: String(source || location.pathname).slice(0, 220),
    stack: String(stack || '').slice(0, 1800),
    request_id: Leon.state.lastRequestId || '',
  });
  if (!message) return;
  try {
    fetch('/api/log/client-error', {
      method: 'POST',
      credentials: 'same-origin',
      keepalive: true,
      headers: Leon.requestHeaders({ method: 'POST' }),
      body: payload,
    }).catch(() => {});
  } catch {}
};

window.addEventListener('error', (event) => {
  Leon.reportClientError('frontend-error', event.message, event.filename, `${event.lineno || ''}:${event.colno || ''}`);
});

window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason;
  const message = String(reason?.message || reason || 'Unhandled promise rejection');
  if (reason?.name === 'AbortError') return;
  if (/^(Load failed|Failed to fetch|NetworkError)/i.test(message) && document.visibilityState !== 'visible') return;
  Leon.reportClientError(
    'frontend-promise',
    message,
    location.pathname,
    reason?.stack || '',
  );
});

Leon.checkStatus = async function checkStatus() {
  try {
    const data = await Leon.api('/api/status', { headers: {} });
    if (!data) return;
    Leon.state.lastStatus = data;
    Leon.state.models = data.models || [];
    Leon.state.fastModels = data.fast_models || [];
    Leon.$('status-dot').className = data.running ? 'online' : 'offline';
    Leon.$('offline-banner').classList.toggle('show', !data.running);
    Leon.updateModelSelect();
    return data;
  } catch {
    Leon.$('status-dot').className = 'offline';
    Leon.$('offline-banner').classList.add('show');
  }
};

Leon.updateModelSelect = function updateModelSelect() {
  const select = Leon.$('model-select');
  const current = Leon.state.currentRoom?.model || 'llama3';
  const models = Leon.state.models.length ? Leon.state.models : [current, 'llama3'];
  const unique = [...new Set(models.concat([current]))];
  select.innerHTML = unique.map(m => `<option value="${Leon.esc(m)}">${Leon.esc(Leon.cleanModel(m))}</option>`).join('');
  select.value = current;
};

window.checkStatus = Leon.checkStatus;
