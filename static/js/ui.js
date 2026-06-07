/** LEON AI – UI helpers, theme, modals, sidebar */
(function () {
  const { state, $, esc, api, checkStatus, cleanModel, fmtTime } = Leon;

  Leon.AVATARS = [
    { id: 'dots', label: 'Punkte' }, { id: 'user', label: 'Profil' }, { id: 'heart', label: 'Herz' },
    { id: 'bolt', label: 'Blitz' }, { id: 'star', label: 'Stern' },
    { id: 'brain', label: 'Brain' }, { id: 'rocket', label: 'Rocket' },
  ];

  Leon.toast = function toast(text) {
    const el = document.createElement('div');
    el.className = 'toast';
    el.textContent = text;
    $('toast').appendChild(el);
    setTimeout(() => el.remove(), 3200);
  };

  Leon.openModal = (id) => $(id).classList.add('show');
  Leon.closeModal = (id) => $(id).classList.remove('show');

  document.addEventListener('click', (e) => {
    if (e.target.classList && e.target.classList.contains('overlay')) {
      e.target.classList.remove('show');
    }
  });

  Leon.applyTheme = function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('leon-theme', theme);
    document.querySelectorAll('[data-theme-toggle]').forEach(btn => {
      btn.textContent = theme === 'dark' ? '☀️' : '🌙';
      btn.title = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
    });
    const hl = $('hljs-theme');
    if (hl) {
      hl.href = theme === 'dark'
        ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css'
        : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
    }
  };

  Leon.toggleTheme = () => Leon.applyTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');

  Leon.setFontSize = function setFontSize(size) {
    document.documentElement.dataset.fontSize = size;
    localStorage.setItem('leon-font-size', size);
    document.querySelectorAll('[data-font-btn]').forEach(b => b.classList.toggle('active', b.dataset.fontBtn === size));
  };

  Leon.applyTopActionsCollapsed = function applyTopActionsCollapsed(collapsed) {
    const wrap = $('top-actions');
    const btn = $('top-collapse-btn');
    if (!wrap || !btn) return;
    wrap.classList.toggle('tools-collapsed', collapsed);
    btn.textContent = collapsed ? '›' : '‹';
    btn.title = collapsed ? 'Werkzeuge ausklappen' : 'Werkzeuge einklappen';
    localStorage.setItem('leon-tools-collapsed', collapsed ? '1' : '0');
  };

  Leon.toggleTopActions = () => Leon.applyTopActionsCollapsed(!$('top-actions')?.classList.contains('tools-collapsed'));

  Leon.applySidebarCollapsed = function applySidebarCollapsed(collapsed) {
    const sb = $('sidebar');
    if (!sb) return;
    sb.classList.toggle('collapsed', collapsed);
    localStorage.setItem('leon-sidebar-collapsed', collapsed ? '1' : '0');
  };

  Leon.toggleSidebarCollapsed = () => Leon.applySidebarCollapsed(!$('sidebar')?.classList.contains('collapsed'));

  Leon.routeFromUrl = function routeFromUrl() {
    const params = new URLSearchParams(location.search);
    const open = params.get('open') || (location.hash || '').replace('#', '');
    if (!open) return;
    setTimeout(() => {
      if (open === 'models' || open === 'assistants') openModelBrowser();
      if (open === 'templates' || open === 'projects') openTemplates();
      if (open === 'library') openLibrary();
      if (open === 'settings') openSettings();
      if (open === 'status') openStatus();
      history.replaceState(null, '', location.pathname);
    }, 300);
  };

  Leon.avatarMarkup = function avatarMarkup(id, small = true) {
    const cls = small ? 'small' : '';
    if (id === 'dots') return `<span class="dot-logo ${cls}"></span>`;
    if (id === 'user') return '<span class="user-symbol"></span>';
    const map = { heart: '♡', bolt: '⚡', star: '✦', brain: '🧠', rocket: '🚀' };
    return `<span class="avatar-symbol">${map[id] || '♡'}</span>`;
  };

  Leon.setAvatar = (id) => { localStorage.setItem('leon-avatar', id); Leon.updateAvatarUi(); };

  Leon.updateAvatarUi = function updateAvatarUi() {
    const id = localStorage.getItem('leon-avatar') || 'dots';
    const brand = $('brand-avatar');
    if (brand) brand.innerHTML = Leon.avatarMarkup(id, true);
    const picker = $('avatar-picker');
    if (picker) {
      picker.innerHTML = Leon.AVATARS.map(a =>
        `<button type="button" class="avatar-choice ${a.id === id ? 'active' : ''}" title="${esc(a.label)}" onclick="setAvatar('${a.id}')">${Leon.avatarMarkup(a.id, false)}</button>`
      ).join('');
    }
  };

  Leon.thinkingHtml = () =>
    '<div class="thinking-bubble"><span class="typing-spinner"></span><span>LEON denkt nach</span><span class="dots">•••</span></div>';

  Leon.renderRooms = function renderRooms(filter = '') {
    const list = $('room-list');
    const q = filter.trim().toLowerCase();
    const rooms = state.rooms.filter(r => !q || String(r.name).toLowerCase().includes(q));
    if (!rooms.length) { list.innerHTML = '<div class="empty">Keine Chats gefunden.</div>'; return; }
    list.innerHTML = rooms.map(r => `
      <button class="room-item ${r.id === state.currentRoomId ? 'active' : ''}" onclick="selectRoom(${r.id})">
        <span class="room-pin ${r.pinned ? 'active' : ''}" onclick="toggleRoomPin(event, ${r.id}, ${r.pinned ? 0 : 1})" title="${r.pinned ? 'Chat lösen' : 'Chat anpinnen'}">★</span>
        <span class="room-name">${esc(r.name)}</span><span class="room-model">${esc(cleanModel(r.model))}</span>
        <span class="room-actions"><span class="mini-btn" onclick="deleteRoom(event, ${r.id})">×</span></span>
      </button>`).join('');
  };

  Leon.updateHeader = function updateHeader() {
    const room = state.currentRoom;
    $('room-title-current').textContent = room?.name || 'Allgemein';
    $('room-meta').textContent = `${cleanModel(room?.model || 'llama3')} · bereit`;
    $('settings-name').value = room?.name || '';
    $('settings-prompt').value = room?.system_prompt || '';
  };

  Leon.loadRooms = async function loadRooms() {
    const data = await api('/api/rooms');
    if (!data) return;
    state.rooms = data;

    if (window.LEON_IS_NEW_LOGIN) {
      window.LEON_IS_NEW_LOGIN = false; // reset
      await createNewRoom();
      return;
    }

    if (!state.currentRoomId || !data.find(r => r.id === state.currentRoomId)) {
      state.currentRoomId = data[0]?.id || null;
    }
    state.currentRoom = data.find(r => r.id === state.currentRoomId) || data[0] || null;
    Leon.renderRooms();
    Leon.updateHeader();
    Leon.updateModelSelect();
  };

  async function selectRoom(id) {
    state.currentRoomId = id;
    state.currentRoom = state.rooms.find(r => r.id === id) || null;
    state.activeLeafId = null;
    document.querySelector('#sidebar')?.classList.remove('open');
    Leon.renderRooms();
    Leon.updateHeader();
    Leon.updateModelSelect();
    await Leon.loadMessages();
  }

  async function createNewRoom() {
    const room = await api('/api/rooms', {
      method: 'POST',
      body: JSON.stringify({ name: 'Neuer Chat', model: state.currentRoom?.model || 'llama3' }),
    });
    if (room) {
      state.currentRoomId = room.id;
      state.activeLeafId = null;
      await Leon.loadRooms();
      await Leon.loadMessages();
      Leon.toast('Neuer Chat erstellt.');
    }
  }

  async function deleteRoom(ev, id) {
    ev.stopPropagation();
    if (state.rooms.length <= 1) { Leon.toast('Mindestens ein Chat muss bleiben.'); return; }
    if (!confirm('Diesen Chat wirklich löschen?')) return;
    await api(`/api/rooms/${id}`, { method: 'DELETE' });
    if (state.currentRoomId === id) state.currentRoomId = null;
    await Leon.loadRooms();
    await Leon.loadMessages();
  }

  async function toggleRoomPin(ev, id, pinned) {
    ev.stopPropagation();
    await api(`/api/rooms/${id}`, { method: 'PATCH', body: JSON.stringify({ pinned: !!pinned }) });
    await Leon.loadRooms();
    Leon.toast(pinned ? 'Chat angepinnt.' : 'Chat gelöst.');
  }

  async function changeModel(model) {
    if (!state.currentRoomId) return;
    await api(`/api/rooms/${state.currentRoomId}/model`, { method: 'POST', body: JSON.stringify({ model }) });
    await Leon.loadRooms();
    Leon.toast('Modell geändert.');
  }

  function openModelBrowser() { Leon.openModal('mod-models'); renderModels(''); }

  function renderModels(filter = '') {
    const q = filter.toLowerCase();
    const installed = new Set(state.models || []);
    const known = (state.fastModels || []).map(m => m.name);
    const all = [...new Set([...(state.models || []), ...known, state.currentRoom?.model || 'llama3'])]
      .filter(Boolean).filter(m => m.toLowerCase().includes(q));
    $('model-list').innerHTML = all.length ? all.map(m => {
      const meta = (state.fastModels || []).find(x => x.name === m) || {};
      const isInstalled = installed.has(m);
      return `<div class="list-item"><div class="list-item-main"><div class="list-item-title">${esc(cleanModel(m))} ${isInstalled ? '· installiert' : ''}</div><div class="list-item-sub">${esc(meta.desc || 'Lokales Ollama-Modell')} ${meta.speed ? '· ' + esc(meta.speed) : ''}</div></div><button class="plain-btn" onclick="useModel('${esc(m)}')">Nutzen</button></div>`;
    }).join('') : '<div class="empty">Kein Modell gefunden.</div>';
  }

  async function useModel(model) { await changeModel(model); Leon.closeModal('mod-models'); }

  async function openTemplates() { Leon.openModal('mod-templates'); await loadTemplates(); }

  async function loadTemplates() {
    const data = await api('/api/templates');
    $('template-list').innerHTML = data && data.length
      ? data.map(t => `<div class="list-item"><div class="list-item-main"><div class="list-item-title">${esc(t.label)}</div><div class="list-item-sub">${esc(t.content).slice(0, 160)}</div></div><button class="plain-btn" onclick="insertTemplate(${t.id})">Einfügen</button><button class="mini-btn" onclick="deleteTemplate(${t.id})">×</button></div>`).join('')
      : '<div class="empty">Noch keine Vorlagen.</div>';
  }

  async function saveTemplate() {
    const label = $('tpl-label').value.trim();
    const content = $('tpl-content').value.trim();
    if (!label || !content) { Leon.toast('Name und Inhalt fehlen.'); return; }
    await api('/api/templates', { method: 'POST', body: JSON.stringify({ label, content, icon: '▱' }) });
    $('tpl-label').value = '';
    $('tpl-content').value = '';
    await loadTemplates();
  }

  function insertTemplate(id) {
    api('/api/templates').then(list => {
      const t = list.find(x => x.id === id);
      if (!t) return;
      $('user-input').value = t.content;
      Leon.autoResize($('user-input'));
      Leon.updateCharCount();
      Leon.closeModal('mod-templates');
      $('user-input').focus();
    });
  }

  async function deleteTemplate(id) { await api(`/api/templates/${id}`, { method: 'DELETE' }); await loadTemplates(); }

  function openLibrary() { Leon.openModal('mod-library'); openFavorites(false); }

  async function openFavorites(showModal = true) {
    if (showModal) Leon.openModal('mod-library');
    const data = await api('/api/favorites');
    $('favorite-list').innerHTML = data && data.length
      ? data.map(f => `<div class="list-item"><div class="list-item-main"><div class="list-item-title">${esc(f.room_name || 'Chat')}</div><div class="list-item-sub">${esc(f.content).slice(0, 240)}</div></div></div>`).join('')
      : '<div class="empty">Noch keine Favoriten.</div>';
  }

  async function openMemory() { Leon.openModal('mod-memory'); await loadMemory(); }

  async function loadMemory() {
    const data = await api(`/api/rooms/${state.currentRoomId}/memory`);
    $('memory-list').innerHTML = data && data.length
      ? data.map(m => `<div class="list-item"><div class="list-item-main"><div class="list-item-sub">${esc(m.fact)}</div></div><button class="mini-btn" onclick="deleteMemory(${m.id})">×</button></div>`).join('')
      : '<div class="empty">Noch nichts gespeichert.</div>';
  }

  async function addMemory() {
    const fact = $('memory-input').value.trim();
    if (!fact) return;
    await api(`/api/rooms/${state.currentRoomId}/memory`, { method: 'POST', body: JSON.stringify({ fact }) });
    $('memory-input').value = '';
    await loadMemory();
  }

  async function deleteMemory(id) {
    await api(`/api/rooms/${state.currentRoomId}/memory/${id}`, { method: 'DELETE' });
    await loadMemory();
  }

  function openSearch() { Leon.openModal('mod-search'); $('search-input').focus(); }

  let searchTimer = null;
  function searchMessages(q) {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(async () => {
      q = q.trim();
      if (!q) { $('search-results').innerHTML = '<div class="empty">Suchbegriff eingeben…</div>'; return; }
      const data = await api(`/api/search?q=${encodeURIComponent(q)}&room_id=${state.currentRoomId}`);
      $('search-results').innerHTML = data && data.length
        ? data.map(r => `<div class="list-item"><div class="list-item-main"><div class="list-item-title">${r.role === 'user' ? 'Du' : 'LEON AI'} · ${fmtTime(r.created)}</div><div class="list-item-sub">${esc(r.content).slice(0, 260)}</div></div></div>`).join('')
        : '<div class="empty">Keine Treffer.</div>';
    }, 220);
  }

  function openExport() { Leon.closeModal('mod-settings'); Leon.openModal('mod-export'); }
  function doExport(fmt) {
    if (state.currentRoomId) {
      window.location.href = `/api/rooms/${state.currentRoomId}/export?format=${encodeURIComponent(fmt)}`;
    }
  }

  function openStatus() { Leon.openModal('mod-status'); renderStatus(); }

  async function renderStatus() {
    const s = await checkStatus();
    $('status-details').innerHTML = `
      <div class="list-item"><div class="list-item-main"><div class="list-item-title">Ollama</div><div class="list-item-sub">${s?.running ? 'Online' : 'Offline'} · http://localhost:11434</div></div></div>
      <div class="list-item"><div class="list-item-main"><div class="list-item-title">Installierte Modelle</div><div class="list-item-sub">${esc((s?.models || []).join(', ') || 'Keine erkannt')}</div></div></div>
      <div class="list-item"><div class="list-item-main"><div class="list-item-title">App</div><div class="list-item-sub">Lokal auf Port 5001 · Login ${s?.auth_enabled ? 'aktiv' : 'aus'}</div></div></div>
      <div class="list-item"><div class="list-item-main"><div class="list-item-title">Status-Legende</div>
        <div class="list-item-sub status-legend">
          <span><i class="legend-dot online"></i>Grün: Ollama ist erreichbar.</span>
          <span><i class="legend-dot wait"></i>Gelb: Verbindung wird geprüft oder ist unklar.</span>
          <span><i class="legend-dot offline"></i>Rot: Ollama/App-Verbindung ist nicht erreichbar.</span>
        </div>
      </div></div>`;
  }

  function openShortcuts() { Leon.openModal('mod-shortcuts'); }
  function focusWorkspace() { $('user-input').focus(); }
  function toggleSidebar() { $('sidebar').classList.toggle('open'); }

  async function openSettings() {
    Leon.updateHeader();
    Leon.setFontSize(document.documentElement.dataset.fontSize || 'md');
    Leon.updateAvatarUi();
    Leon.openModal('mod-settings');
  }

  async function saveSettings() {
    await api(`/api/rooms/${state.currentRoomId}`, {
      method: 'PATCH',
      body: JSON.stringify({
        name: $('settings-name').value.trim() || 'Neuer Chat',
        system_prompt: $('settings-prompt').value.trim(),
      }),
    });
    await Leon.loadRooms();
    Leon.closeModal('mod-settings');
    Leon.toast('Einstellungen gespeichert.');
  }

  async function clearCurrentRoom() {
    if (!confirm('Verlauf in diesem Chat wirklich löschen?')) return;
    await api(`/api/rooms/${state.currentRoomId}/clear`, { method: 'POST', body: '{}' });
    await Leon.loadMessages();
    Leon.closeModal('mod-settings');
    Leon.toast('Verlauf gelöscht.');
  }

  Leon.autoResize = function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 140) + 'px';
  };

  Leon.updateCharCount = function updateCharCount() {
    const n = $('user-input').value.length;
    $('char-count').textContent = n ? `${n}` : '';
  };

  // Expose onclick handlers globally
  Object.assign(window, {
    toggleTheme: Leon.toggleTheme,
    toggleTopActions: Leon.toggleTopActions,
    toggleSidebarCollapsed: Leon.toggleSidebarCollapsed,
    setAvatar: Leon.setAvatar,
    setFontSize: Leon.setFontSize,
    applyTheme: Leon.applyTheme,
    openModal: Leon.openModal,
    closeModal: Leon.closeModal,
    selectRoom,
    createNewRoom,
    deleteRoom,
    toggleRoomPin,
    changeModel,
    openModelBrowser,
    renderModels,
    useModel,
    openTemplates,
    saveTemplate,
    insertTemplate,
    deleteTemplate,
    openLibrary,
    openFavorites,
    openMemory,
    addMemory,
    deleteMemory,
    openSearch,
    searchMessages,
    openExport,
    doExport,
    openStatus,
    openShortcuts,
    focusWorkspace,
    toggleSidebar,
    openSettings,
    saveSettings,
    clearCurrentRoom,
  });
})();
