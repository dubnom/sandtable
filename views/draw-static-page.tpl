<table class="main">
 <tr>
  <td id="methodPane" valign="TOP" style="width: 95px;">
   <div id="methodScroll" style="height: 300px; overflow-y: auto; overflow-x: hidden; scrollbar-gutter: stable;">
   <div id="methodGrid" style="display: grid; grid-template-columns: repeat(auto-fill, 79px); gap: 4px; justify-content: start;"></div>
   </div>
   <div id="statusMsg" class="navigation" style="margin-top: 12px;"></div>
  </td>
  <td valign="TOP">
   <center>
    <img id="planImage" class="plan" src="{{ imagefile }}" width="{{ width }}" height="{{ height }}"><br>
    <div id="errorBox" class="error" style="display: none;"></div>
    <span id="drawInfo" class="drawtime"></span>
    <div id="dialogHost"></div>
    <div style="margin-top: 10px; line-height: 1.8;">
     <button id="redrawBtn" class="redraw" type="button">Redraw Screen</button>
     <button id="randomBtn" class="random" type="button">Random!</button>
     <button id="drawBtn" class="doit" type="button">Draw in Sand!</button>
    </div>
    <div class="savebox" style="margin-top: 10px;">
     <span class="save">Name</span>
     <input id="nameInput" class="save" type="text" size="24">
     <button id="saveBtn" class="save" type="button">Save</button>
     <button id="exportBtn" class="export" type="button">Export</button>
      <button id="playlistBtn" class="load" type="button">Add to Playlist</button>
    </div>
   </center>
  </td>
 </tr>
</table>

<style>
 #methodGrid img.sandable {
  border: 1px solid #6f6f6f;
  box-sizing: border-box;
 }

 #methodGrid img.selected {
  border: 3px solid #ffd24d;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.85), 0 0 10px rgba(255, 210, 77, 0.85);
  box-sizing: border-box;
 }
</style>

<script>
(function() {
  if (typeof window.__sandtablePageCleanup === 'function') {
    try {
      window.__sandtablePageCleanup();
    } catch (err) {
      console.error(err);
    }
  }

  const initialMethod = {{ method|tojson }};
  const initialLoadName = {{ loadname|default('', true)|tojson }};
  const initialParams = {{ initial_params|default({}, true)|tojson }};
  const fallbackMethods = {{ sandables|tojson }};
  const isEmbedded = {{ embedded|tojson }};
  const pagePath = window.location.pathname || '/draw';
  const appBasePath = pagePath.replace(/\/draw\/?$/, '').replace(/\/$/, '');

  // Initialize WebSocket connection
  let socket = io({
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5,
    transports: ['websocket'],
    path: (appBasePath ? appBasePath : '') + '/socket.io'
  });

  function buildUrl(path) {
    if (appBasePath) {
      return appBasePath + path;
    }
    return path;
  }

  function drawUrlForMethod(method) {
    if (appBasePath) {
      return appBasePath + '/draw?method=' + encodeURIComponent(method);
    }
    return '/draw?method=' + encodeURIComponent(method);
  }

  const state = {
    method: initialMethod,
    methods: fallbackMethods || [],
    fields: [],
    params: {},
    realtime: true,
    latestPreviewRequestId: 0,
    pendingPreviewRequests: {},
    pendingPreviewByKey: {},
    realtimeTimer: null,
    methodLoadInFlight: false,
  };
  let destroyed = false;

  const methodGrid = document.getElementById('methodGrid');
  const methodPane = document.getElementById('methodPane');
  const methodScroll = document.getElementById('methodScroll');
  const planImage = document.getElementById('planImage');
  const errorBox = document.getElementById('errorBox');
  const drawInfo = document.getElementById('drawInfo');
  const dialogHost = document.getElementById('dialogHost');
  const statusMsg = document.getElementById('statusMsg');
  const nameInput = document.getElementById('nameInput');

  const METHOD_TILE_WIDTH = 79;
  const METHOD_TILE_GAP = 4;
  const METHOD_MIN_WIDTH = 95;
  const METHOD_MAX_WIDTH = 280;
  const STATUSBAR_MARGIN = 8;

  function methodGridWidth(columns) {
    return (columns * METHOD_TILE_WIDTH) + (Math.max(columns - 1, 0) * METHOD_TILE_GAP);
  }

  function layoutMethodPane() {
    if (!methodPane || !methodScroll || !methodGrid) {
      return;
    }

    const top = methodScroll.getBoundingClientRect().top;
    let bottom = window.innerHeight - STATUSBAR_MARGIN;
    const globalStatusBar = document.getElementById('globalStatusBar');
    if (globalStatusBar) {
      const barRect = globalStatusBar.getBoundingClientRect();
      if (barRect.top > 0) {
        bottom = Math.min(bottom, barRect.top - STATUSBAR_MARGIN);
      }
    }
    const availableHeight = Math.max(140, Math.floor(bottom - top));
    methodScroll.style.height = String(availableHeight) + 'px';

    const preferredWidth = Math.min(METHOD_MAX_WIDTH, Math.max(METHOD_MIN_WIDTH, Math.floor(window.innerWidth * 0.18)));
    let columns = Math.max(1, Math.floor((preferredWidth + METHOD_TILE_GAP) / (METHOD_TILE_WIDTH + METHOD_TILE_GAP)));
    if (state.methods.length) {
      columns = Math.min(columns, state.methods.length);
    }

    const snappedGridWidth = methodGridWidth(columns);
    const scrollbarWidth = Math.max(methodScroll.offsetWidth - methodScroll.clientWidth, 14);
    const snappedPaneWidth = snappedGridWidth + scrollbarWidth;
    methodPane.style.width = String(snappedPaneWidth) + 'px';
    methodGrid.style.gridTemplateColumns = 'repeat(' + columns + ', ' + METHOD_TILE_WIDTH + 'px)';
  }

  function twoDigit(value) {
    return String(value).padStart(2, '0');
  }

  function makeDefaultFileName(method) {
    const now = new Date();
    const stamp = String(now.getFullYear()) +
      twoDigit(now.getMonth() + 1) +
      twoDigit(now.getDate()) + '_' +
      twoDigit(now.getHours()) +
      twoDigit(now.getMinutes()) +
      twoDigit(now.getSeconds());
    const safeMethod = String(method || 'drawing').replace(/[^A-Za-z0-9_-]+/g, '_');
    return safeMethod + '_' + stamp;
  }

  function refreshDefaultFileName() {
    const previousAutoName = state.autoFileName || '';
    state.autoFileName = makeDefaultFileName(state.method);
    if (!nameInput.value || nameInput.value === previousAutoName) {
      nameInput.value = state.autoFileName;
    }
  }

  function methodImageUrl(method) {
    return buildUrl('/images/' + encodeURIComponent(method) + '.png');
  }

  function methodsEqual(left, right) {
    const a = Array.isArray(left) ? left : [];
    const b = Array.isArray(right) ? right : [];
    if (a.length !== b.length) {
      return false;
    }
    for (let i = 0; i < a.length; i += 1) {
      if (a[i] !== b[i]) {
        return false;
      }
    }
    return true;
  }

  function updateMethodSelection() {
    const images = methodGrid.querySelectorAll('img[data-method-name]');
    images.forEach(function(image) {
      const isSelected = image.dataset.methodName === state.method;
      image.className = isSelected ? 'selected' : 'sandable';
    });
  }

  function populateMethods(methods) {
    const nextMethods = Array.isArray(methods) ? methods.slice() : [];
    if (methodsEqual(state.methods, nextMethods) && methodGrid.childElementCount) {
      state.methods = nextMethods;
      updateMethodSelection();
      layoutMethodPane();
      return;
    }

    state.methods = nextMethods;
    methodGrid.innerHTML = '';
    nextMethods.forEach(function(method) {
      const link = document.createElement('a');
      link.href = '#';
      link.title = method;
      link.style.display = 'block';

      const image = document.createElement('img');
      image.dataset.methodName = method;
      image.src = methodImageUrl(method);
      image.width = 75;
      image.height = 60;
      image.loading = 'lazy';
      image.decoding = 'async';
      image.alt = method;
      image.className = method === state.method ? 'selected' : 'sandable';
      link.appendChild(image);

      link.addEventListener('click', function(event) {
        event.preventDefault();
        event.stopPropagation();
        selectMethod(method);
      });

      methodGrid.appendChild(link);
    });
    layoutMethodPane();
  }

  function setStatus(msg) {
    if (destroyed) {
      return;
    }
    statusMsg.textContent = msg || '';
  }

  function showError(msg) {
    if (destroyed) {
      return;
    }
    if (msg) {
      errorBox.style.display = 'block';
      errorBox.textContent = 'Error: ' + msg;
    } else {
      errorBox.style.display = 'none';
      errorBox.textContent = '';
    }
  }

  function renderDrawInfo(summary) {
    const info = (summary && summary.drawinfo) ? String(summary.drawinfo) : '';
    const helpPath = (summary && summary.helpUrl) ? String(summary.helpUrl) : '';

    drawInfo.innerHTML = '';
    if (!info && !helpPath) {
      return;
    }

    if (info) {
      drawInfo.appendChild(document.createTextNode(info));
    }

    if (helpPath) {
      if (info) {
        drawInfo.appendChild(document.createTextNode('    '));
      }
      const link = document.createElement('a');
      link.href = buildUrl('/' + helpPath.replace(/^\/+/, ''));
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
      link.className = 'navigation';
      link.textContent = 'Help!';
      drawInfo.appendChild(link);
    }
  }

  async function fetchJson(url, options) {
    const response = await fetch(url, options || {});
    const payload = await response.json();
    if (!response.ok) {
      const err = new Error(payload.error || 'Request failed');
      err.payload = payload;
      throw err;
    }
    return payload;
  }

  function valueForChoiceField(field, rawValue) {
    const kind = field.kind;
    const choices = field.choices || [];
    if ((kind === 'DialogYesNo' || kind === 'DialogTrueFalse' || kind === 'DialogOnOff' || kind === 'Dialog2Choices') && choices.length >= 2) {
      if (rawValue === true || rawValue === 1 || rawValue === '1' || rawValue === 'true' || rawValue === 'True') {
        return choices[1];
      }
      if (rawValue === false || rawValue === 0 || rawValue === '0' || rawValue === 'false' || rawValue === 'False') {
        return choices[0];
      }
    }
    return rawValue;
  }

  function controlForField(field, value) {
    const kind = field.kind;

    if (kind === 'DialogBreak') {
      const hr = document.createElement('hr');
      return hr;
    }

    if (kind === 'DialogList' || kind === 'DialogYesNo' || kind === 'DialogTrueFalse' || kind === 'DialogOnOff' || kind === 'Dialog2Choices') {
      const select = document.createElement('select');
      select.dataset.fieldName = field.name;
      const choices = field.choices || [];
      let selectedValue = value;
      if ((kind === 'DialogYesNo' || kind === 'DialogTrueFalse' || kind === 'DialogOnOff' || kind === 'Dialog2Choices') && choices.length >= 2) {
        if (value === true || value === 1 || value === '1' || value === 'true' || value === 'True') {
          selectedValue = choices[1];
        } else if (value === false || value === 0 || value === '0' || value === 'false' || value === 'False') {
          selectedValue = choices[0];
        }
      }
      choices.forEach(function(choice) {
        const opt = document.createElement('option');
        opt.value = String(choice);
        opt.textContent = String(choice);
        if (String(choice) === String(selectedValue)) {
          opt.selected = true;
        }
        select.appendChild(opt);
      });
      return select;
    }

    if (kind === 'DialogFont' || kind === 'DialogFileList') {
      const select = document.createElement('select');
      select.dataset.fieldName = field.name;
      const choices = field.choices || [];
      choices.forEach(function(choice) {
        const opt = document.createElement('option');
        const displayName = Array.isArray(choice) ? choice[0] : String(choice);
        const filePath = Array.isArray(choice) ? choice[1] : String(choice);
        opt.value = filePath;
        opt.textContent = displayName;
        if (filePath === String(value)) {
          opt.selected = true;
        }
        select.appendChild(opt);
      });
      return select;
    }

    if (kind === 'DialogMulti') {
      const ta = document.createElement('textarea');
      ta.dataset.fieldName = field.name;
      ta.rows = field.rows || 5;
      ta.cols = field.cols || 20;
      ta.value = value == null ? '' : String(value);
      return ta;
    }

    if (kind === 'DialogColor') {
      const input = document.createElement('input');
      input.type = 'color';
      input.dataset.fieldName = field.name;
      input.value = '#ffffff';
      if (Array.isArray(value) && value.length === 3) {
        const r = Number(value[0]).toString(16).padStart(2, '0');
        const g = Number(value[1]).toString(16).padStart(2, '0');
        const b = Number(value[2]).toString(16).padStart(2, '0');
        input.value = '#' + r + g + b;
      }
      return input;
    }

    const input = document.createElement('input');
    input.dataset.fieldName = field.name;

    if (kind === 'DialogInt' || kind === 'DialogFloat') {
      input.type = 'number';
      if (field.min !== undefined && field.min !== null) {
        input.min = field.min;
      }
      if (field.max !== undefined && field.max !== null) {
        input.max = field.max;
      }
      if (kind === 'DialogInt') {
        input.step = '1';
      } else if (field.step !== undefined && field.step !== null) {
        input.step = String(field.step);
      } else {
        input.step = 'any';
      }

      input.value = value == null ? '' : String(value);

      const useSlider = field.slider === true && field.min !== undefined && field.min !== null && field.max !== undefined && field.max !== null;
      if (!useSlider) {
        return input;
      }

      const wrapper = document.createElement('span');
      wrapper.appendChild(input);

      const slider = document.createElement('input');
      slider.type = 'range';
      slider.dataset.fieldName = field.name;
      slider.dataset.fieldSliderName = field.name;
      slider.min = String(field.min);
      slider.max = String(field.max);
      if (kind === 'DialogInt') {
        slider.step = '1';
      } else if (field.step !== undefined && field.step !== null) {
        slider.step = String(field.step);
      }
      slider.value = input.value;
      slider.style.marginLeft = '6px';
      slider.style.verticalAlign = 'middle';

      input.addEventListener('input', function() {
        slider.value = input.value;
      });
      input.addEventListener('change', function() {
        slider.value = input.value;
      });
      slider.addEventListener('input', function() {
        input.value = slider.value;
      });
      slider.addEventListener('change', function() {
        input.value = slider.value;
      });

      wrapper.appendChild(slider);
      return wrapper;
    }

    input.type = 'text';
    input.value = value == null ? '' : String(value);
    if (kind === 'DialogStr' && field.length) {
      input.size = field.length;
    }
    return input;
  }

  function renderDialog() {
    if (destroyed) {
      return;
    }
    const table = document.createElement('table');
    table.className = 'form';

    state.fields.forEach(function(field) {
      const row = document.createElement('tr');

      const labelCell = document.createElement('td');
      labelCell.setAttribute('align', 'right');
      const labelSpan = document.createElement('span');
      labelSpan.className = 'form';
      labelSpan.textContent = field.prompt || '';
      labelCell.appendChild(labelSpan);
      row.appendChild(labelCell);

      const valueCell = document.createElement('td');
      const valueSpan = document.createElement('span');
      valueSpan.className = 'form';

      const value = Object.prototype.hasOwnProperty.call(state.params, field.name) ? state.params[field.name] : field.default;
      const control = controlForField(field, value);
      valueSpan.appendChild(control);
      if (field.randomizable) {
        const randomButton = document.createElement('button');
        randomButton.type = 'button';
        randomButton.textContent = 'Rnd';
        randomButton.title = 'Randomize this field';
        randomButton.dataset.randomFieldName = field.name;
        randomButton.style.marginLeft = '6px';
        randomButton.style.fontSize = '11px';
        randomButton.style.padding = '1px 5px';
        valueSpan.appendChild(randomButton);
      }
      if (field.name && field.kind !== 'DialogBreak') {
        const defaultButton = document.createElement('button');
        defaultButton.type = 'button';
        defaultButton.textContent = 'Def';
        defaultButton.title = 'Restore default value';
        defaultButton.dataset.defaultFieldName = field.name;
        defaultButton.style.marginLeft = '6px';
        defaultButton.style.fontSize = '11px';
        defaultButton.style.padding = '1px 5px';
        valueSpan.appendChild(defaultButton);
      }
      if (field.units) {
        valueSpan.appendChild(document.createTextNode(' ' + field.units));
      }
      valueCell.appendChild(valueSpan);
      row.appendChild(valueCell);

      table.appendChild(row);
    });

    dialogHost.innerHTML = '';
    dialogHost.appendChild(table);
  }

  function updateDialogValues(params) {
    if (destroyed) {
      return;
    }
    state.fields.forEach(function(field) {
      if (!field.name) {
        return;
      }
      const value = Object.prototype.hasOwnProperty.call(params, field.name) ? params[field.name] : field.default;
      const node = dialogHost.querySelector('[data-field-name="' + field.name.replace(/"/g, '\\"') + '"]');
      if (!node) {
        return;
      }
      if (field.kind === 'DialogColor' && Array.isArray(value) && value.length === 3) {
        const r = Number(value[0]).toString(16).padStart(2, '0');
        const g = Number(value[1]).toString(16).padStart(2, '0');
        const b = Number(value[2]).toString(16).padStart(2, '0');
        node.value = '#' + r + g + b;
      } else if (field.kind === 'DialogYesNo' || field.kind === 'DialogTrueFalse' || field.kind === 'DialogOnOff' || field.kind === 'Dialog2Choices') {
        node.value = String(valueForChoiceField(field, value));
      } else {
        node.value = value == null ? '' : String(value);
      }
      const sliderNode = dialogHost.querySelector('[data-field-slider-name="' + field.name.replace(/"/g, '\\"') + '"]');
      if (sliderNode) {
        sliderNode.value = node.value;
      }
    });
  }

  function collectParams() {
    const params = {};
    state.fields.forEach(function(field) {
      if (!field.name) {
        return;
      }
      const node = dialogHost.querySelector('[data-field-name="' + field.name.replace(/"/g, '\\"') + '"]');
      if (!node) {
        return;
      }
      params[field.name] = node.value;
    });
    return params;
  }

  function applyPreviewData(data) {
    const previousMethod = state.method;
    if (data.method) {
      state.method = data.method;
    }
    if (state.method !== previousMethod) {
      refreshDefaultFileName();
    }
    if (typeof data.realtime === 'boolean') {
      state.realtime = data.realtime;
    }
    const schemaChanged = Array.isArray(data.fields);
    if (schemaChanged) {
      state.fields = data.fields;
    }
    const newParams = data.params || {};
    state.params = newParams;
    if (data.image && data.image.dataUrl) {
      planImage.src = data.image.dataUrl;
    } else if (data.image && data.image.url) {
      planImage.src = data.image.url;
    }
    const summary = data.summary || {};
    renderDrawInfo(summary);
    showError(data.errors || '');
    if (schemaChanged) {
      renderDialog();
    } else {
      updateDialogValues(newParams);
    }
  }

  async function loadMethods() {
    const data = await fetchJson(buildUrl('/api/draw/methods?method=' + encodeURIComponent(state.method)));
    state.methods = data.methods || [];
    populateMethods(state.methods);
  }

  async function loadDrawing(name) {
    const loadName = String(name || '').trim();
    if (!loadName) {
      return;
    }
    setStatus('Loading drawing...');
    const data = await fetchJson(buildUrl('/api/draw/load'), {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({name: loadName}),
    });
    applyPreviewData(data);
    populateMethods(state.methods);
    if (data && data.loadedName) {
      nameInput.value = String(data.loadedName);
      state.autoFileName = String(data.loadedName);
    }
  }

  function loadSchema(method) {
    return new Promise(function(resolve, reject) {
      socket.once('draw:schema:response', function(data) {
        if (data.error) {
          reject(new Error(data.error || 'Schema load failed'));
          return;
        }

        state.method = data.method;
        state.realtime = data.realtime !== false;
        state.fields = data.fields || [];
        state.params = {};
        state.fields.forEach(function(field) {
          if (field.name) {
            state.params[field.name] = field.default;
          }
        });
        if (!isEmbedded) {
          window.history.replaceState(null, '', drawUrlForMethod(state.method));
        }
        refreshDefaultFileName();
        renderDialog();
        resolve(data);
      });

      socket.emit('draw:schema', {method: method});
    });
  }

  function cancelRealtimePreview() {
    if (state.realtimeTimer) {
      clearTimeout(state.realtimeTimer);
      state.realtimeTimer = null;
    }
  }

  function realtimePreview() {
    const DELAY_MS = 250;
    if (!state.realtime || state.methodLoadInFlight) {
      return;
    }
    cancelRealtimePreview();
    state.realtimeTimer = setTimeout(function() {
      state.realtimeTimer = null;
      preview('refresh');
    }, DELAY_MS);
  }

  async function selectMethod(method) {
    if (state.methodLoadInFlight) {
      return;
    }
    setStatus('Loading method...');
    state.methodLoadInFlight = true;
    cancelRealtimePreview();
    try {
      await preview('refresh', {method: method, includeFields: true});
      populateMethods(state.methods);
    } catch (err) {
      showError(err.message || 'Method load failed');
      setStatus('');
    } finally {
      state.methodLoadInFlight = false;
    }
  }

  // WebSocket-based interactive requests
  function preview(action, extraPayload) {
    setStatus('Working...');
    const payload = Object.assign({
      method: state.method,
      action: action || 'refresh',
      params: collectParams(),
    }, extraPayload || {});

    const dedupeKey = JSON.stringify({
      method: payload.method,
      action: payload.action,
      params: payload.params,
      fieldName: payload.fieldName || null,
      includeFields: !!payload.includeFields,
    });
    const existingRequestId = state.pendingPreviewByKey[dedupeKey];
    if (existingRequestId && state.pendingPreviewRequests[existingRequestId]) {
      return state.pendingPreviewRequests[existingRequestId].promise;
    }

    state.latestPreviewRequestId += 1;
    const requestId = state.latestPreviewRequestId;
    payload.requestId = requestId;

    let resolvePending;
    const promise = new Promise(function(resolve) {
      resolvePending = resolve;
    });
    state.pendingPreviewRequests[requestId] = {
      resolve: resolvePending,
      key: dedupeKey,
      promise: promise,
    };
    state.pendingPreviewByKey[dedupeKey] = requestId;

    socket.emit('draw:preview', payload);
    return promise;
  }

  function randomizeField(fieldName) {
    preview('random-field', {fieldName: fieldName});
  }

  function restoreFieldDefault(fieldName) {
    const field = (state.fields || []).find(function(f) { return f.name === fieldName; });
    if (!field) {
      return;
    }
    const node = dialogHost.querySelector('[data-field-name="' + fieldName.replace(/"/g, '\\"') + '"]');
    if (!node) {
      return;
    }

    let defaultValue = field.default;
    if (node.tagName === 'SELECT') {
      defaultValue = valueForChoiceField(field, defaultValue);
      node.value = defaultValue == null ? '' : String(defaultValue);
    } else if (field.kind === 'DialogColor' && Array.isArray(defaultValue) && defaultValue.length === 3) {
      const r = Number(defaultValue[0]).toString(16).padStart(2, '0');
      const g = Number(defaultValue[1]).toString(16).padStart(2, '0');
      const b = Number(defaultValue[2]).toString(16).padStart(2, '0');
      node.value = '#' + r + g + b;
    } else {
      node.value = defaultValue == null ? '' : String(defaultValue);
    }

    const sliderNode = dialogHost.querySelector('[data-field-slider-name="' + fieldName.replace(/"/g, '\\"') + '"]');
    if (sliderNode) {
      sliderNode.value = node.value;
    }

    preview('refresh');
  }

  socket.on('draw:preview:response', function(data) {
    if (destroyed) {
      return;
    }
    const responseRequestId = data && data.requestId;
    if (responseRequestId && state.pendingPreviewRequests[responseRequestId]) {
      const pending = state.pendingPreviewRequests[responseRequestId];
      pending.resolve(data);
      if (pending.key && state.pendingPreviewByKey[pending.key] === responseRequestId) {
        delete state.pendingPreviewByKey[pending.key];
      }
      delete state.pendingPreviewRequests[responseRequestId];
    }
    if (data && data.requestId && data.requestId !== state.latestPreviewRequestId) {
      return;
    }
    if (data.error) {
      showError(data.error);
      setStatus('');
    } else {
      applyPreviewData(data);
      setStatus('');
    }
  });

  function executeDraw() {
    setStatus('Sending to machine...');
    socket.emit('draw:execute', {
      method: state.method,
      params: collectParams(),
    });
  }

  socket.on('draw:execute:response', function(data) {
    if (destroyed) {
      return;
    }
    if (data.error) {
      showError(data.error);
      setStatus('');
    } else if (data.status === 'ok') {
      if (data.image && data.image.dataUrl) {
        planImage.src = data.image.dataUrl;
      } else if (data.image && data.image.url) {
        planImage.src = data.image.url;
      }
      setStatus('Draw started');
      showError('');
    }
  });

  function saveDrawing() {
    setStatus('Saving...');
    socket.emit('draw:save', {
      method: state.method,
      name: nameInput.value || state.autoFileName || '',
      params: collectParams(),
    });
  }

  socket.on('draw:save:response', function(data) {
    if (destroyed) {
      return;
    }
    if (data.error) {
      showError(data.error);
      setStatus('');
    } else if (data.status === 'ok') {
      setStatus('Saved');
      showError('');
    }
  });

  function exportDrawing() {
    setStatus('Exporting...');
    socket.emit('draw:export', {
      method: state.method,
      name: nameInput.value || state.autoFileName || '',
      params: collectParams(),
    });
  }

  function addToPlaylist() {
    setStatus('Adding to playlist...');
    socket.emit('draw:playlist:add', {
      method: state.method,
      params: collectParams(),
    });
  }

  socket.on('draw:export:response', function(data) {
    if (destroyed) {
      return;
    }
    if (data.error) {
      showError(data.error);
      setStatus('');
    } else if (data.status === 'ok') {
      setStatus('Exported');
      showError('');
    }
  });

  socket.on('draw:playlist:add:response', function(data) {
    if (destroyed) {
      return;
    }
    if (data.error || data.status !== 'ok') {
      showError((data && data.error) ? data.error : 'Unable to add to playlist');
      setStatus('');
    } else {
      const title = data.item && data.item.title ? String(data.item.title) : 'playlist';
      setStatus('Added: ' + title);
      showError('');
    }
  });

  // WebSocket connection handlers
  socket.on('connect', function() {
    if (destroyed) {
      return;
    }
    setStatus('Connected');
  });

  socket.on('disconnect', function() {
    if (destroyed) {
      return;
    }
    setStatus('Disconnected - attempting to reconnect');
  });

  socket.on('connect_error', function(error) {
    if (destroyed) {
      return;
    }
    showError('Connection error: ' + error.message);
  });

  window.__sandtablePageCleanup = function() {
    destroyed = true;
    cancelRealtimePreview();
    state.pendingPreviewRequests = {};
    state.pendingPreviewByKey = {};
    window.removeEventListener('resize', layoutMethodPane);
    try {
      socket.disconnect();
    } catch (err) {
      console.error(err);
    }
  };

  document.getElementById('redrawBtn').addEventListener('click', function() {
    preview('refresh');
  });
  document.getElementById('randomBtn').addEventListener('click', function() {
    preview('random');
  });
  document.getElementById('drawBtn').addEventListener('click', executeDraw);
  document.getElementById('saveBtn').addEventListener('click', saveDrawing);
  document.getElementById('exportBtn').addEventListener('click', exportDrawing);
  document.getElementById('playlistBtn').addEventListener('click', addToPlaylist);

  dialogHost.addEventListener('change', function(event) {
    if (event.target && event.target.dataset && event.target.dataset.fieldName) {
      realtimePreview();
    }
  });

  function isDeferredTypingField(target) {
    if (!target || !target.dataset || !target.dataset.fieldName) {
      return false;
    }
    if (target.tagName === 'TEXTAREA') {
      return true;
    }
    if (target.tagName !== 'INPUT') {
      return false;
    }
    const inputType = (target.type || '').toLowerCase();
    return inputType === 'text' || inputType === 'number';
  }

  dialogHost.addEventListener('input', function(event) {
    if (event.target && event.target.dataset && event.target.dataset.fieldName) {
      if (isDeferredTypingField(event.target)) {
        return;
      }
      realtimePreview();
    }
  });

  dialogHost.addEventListener('keydown', function(event) {
    if (event.key !== 'Enter') {
      return;
    }
    if (!isDeferredTypingField(event.target)) {
      return;
    }
    if (event.target.tagName === 'INPUT') {
      event.preventDefault();
    }
    realtimePreview();
  });

  dialogHost.addEventListener('mousedown', function(event) {
    if (event.button !== 0) {
      return;
    }
    if (event.target && event.target.dataset && event.target.dataset.randomFieldName) {
      event.preventDefault();
      randomizeField(event.target.dataset.randomFieldName);
    }
    if (event.target && event.target.dataset && event.target.dataset.defaultFieldName) {
      event.preventDefault();
      restoreFieldDefault(event.target.dataset.defaultFieldName);
    }
  });

  (async function init() {
    try {
      window.addEventListener('resize', layoutMethodPane);

      // Initialize a sane default save/export name before first preview response.
      refreshDefaultFileName();

      // Always show a method list immediately, even if API calls fail.
      populateMethods(state.methods);

      try {
        await loadMethods();
      } catch (err) {
        setStatus('Using built-in method list');
      }

      if (initialLoadName) {
        await loadDrawing(initialLoadName);
      } else {
        const initialPreviewPayload = {includeFields: true};
        if (initialParams && Object.keys(initialParams).length) {
          initialPreviewPayload.params = initialParams;
        }
        await preview('refresh', initialPreviewPayload);
      }
    } catch (err) {
      showError(err.message || 'Initialization failed');
      setStatus('Initialization failed');
    }
  })();
})();
</script>
