<table class="main">
 <tr>
  <td id="methodGridCell" valign="TOP" style="width: 247px;">
    <div id="methodGridScroller" style="overflow-y: scroll; overflow-x: hidden; overscroll-behavior: contain; scrollbar-gutter: stable; -webkit-overflow-scrolling: touch; width: fit-content; height: calc(100vh - 170px); min-height: 160px;">
       <div id="methodGrid" style="display: grid; grid-template-columns: repeat(3, 79px); gap: 4px;"></div>
     </div>
   <div id="statusMsg" class="navigation" style="margin-top: 12px;"></div>
  </td>
  <td id="drawDialogCell" valign="TOP">
   <center>
    <img id="planImage" class="plan" src="" width="{{ width }}" height="{{ height }}"><br>
    <div id="errorBox" class="error" style="display: none;"></div>
    <span id="drawInfo" class="drawtime"></span>
    <div id="dialogHost"></div>
    <div style="margin-top: 10px; line-height: 1.8;">
      <button id="redrawBtn" class="redraw" type="button">Refresh</button>
     <button id="randomBtn" class="random" type="button">Random!</button>
      <button id="defaultsBtn" class="defaults" type="button">Defaults</button>
      <button id="drawBtn" class="doit" type="button">Draw Now!</button>
      <button id="playlistBtn" class="load" type="button">Add to Playlist</button>
    </div>
    <div class="savebox" style="margin-top: 10px;">
      <button id="saveBtn" class="save" type="button">Save...</button>
      <button id="exportBtn" class="export" type="button">Export...</button>
    </div>
   </center>
  </td>
 </tr>
</table>

<script src="//cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
(function() {
  if (typeof window.__sandtablePageCleanup === 'function') {
    try {
      window.__sandtablePageCleanup();
    } catch (err) {
      console.error(err);
    }
  }

  const LOADING_SRC = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='{{ width }}' height='{{ height }}'%3E%3Crect width='100%25' height='100%25' fill='%23e8e4da'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='20' fill='%23888'%3ELoading...%3C/text%3E%3C/svg%3E";
  const initialMethod = {{ method|tojson }};
  const initialParams = {{ initial_params|default({}, true)|tojson }};
  const initialLoadname = {{ loadname|default('')|tojson }};
  const fallbackMethods = {{ sandables|tojson }};
  const pagePath = window.location.pathname || '/draw';
  const appBasePath = pagePath.replace(/\/draw\/?$/, '').replace(/\/$/, '');

  // Initialize WebSocket connection
  let socket = io({
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5,
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

  // Restore state saved from a previous visit to the draw page
  // initialParams being non-empty means the user navigated here with explicit intent (e.g. filer click).
  // In that case, ignore any saved draw state so the requested file/method loads correctly.
  const _hasExplicitParams = initialParams && Object.keys(initialParams).length > 0;
  const _savedDraw = (!_hasExplicitParams && window.__sandtableSavedDraw) ? window.__sandtableSavedDraw : null;
  window.__sandtableSavedDraw = null;

  const state = {
    method: (_savedDraw && _savedDraw.method) ? _savedDraw.method : initialMethod,
    methods: fallbackMethods || [],
    fields: [],
    params: {},
    realtime: true,
    latestPreviewRequestId: 0,
    lastPreviewSignature: '',
    lastPreviewAt: 0,
    switchRequestId: null,
    switchBusyTimer: null,
  };

  const methodGrid = document.getElementById('methodGrid');
  const methodGridCell = document.getElementById('methodGridCell');
  const methodGridScroller = document.getElementById('methodGridScroller');
  const drawDialogCell = document.getElementById('drawDialogCell');
  const planImage = document.getElementById('planImage');
  const errorBox = document.getElementById('errorBox');
  const drawInfo = document.getElementById('drawInfo');
  const dialogHost = document.getElementById('dialogHost');
  const statusMsg = document.getElementById('statusMsg');
  const redrawBtn = document.getElementById('redrawBtn');

  planImage.src = LOADING_SRC;

  function methodImageUrl(method) {
    return buildUrl('/images/' + encodeURIComponent(method) + '.png');
  }

  function updateMethodSelection(newMethod) {
    const images = methodGrid.querySelectorAll('img');
    images.forEach(function(img) {
      img.className = img.alt === newMethod ? 'selected' : 'sandable';
    });
  }

  function populateMethods(methods) {
    const previousScrollTop = methodGridScroller ? methodGridScroller.scrollTop : 0;
    methodGrid.innerHTML = '';
    (methods || []).forEach(function(method) {
      const link = document.createElement('a');
      link.href = drawUrlForMethod(method);
      link.title = method;
      link.style.display = 'block';

      const image = document.createElement('img');
      image.src = methodImageUrl(method);
      image.width = 75;
      image.height = 60;
      image.alt = method;
      image.className = method === state.method ? 'selected' : 'sandable';
      link.appendChild(image);

      link.addEventListener('click', function(event) {
        event.preventDefault();
        selectMethod(method);
      });

      methodGrid.appendChild(link);
    });
    if (methodGridScroller) {
      methodGridScroller.scrollTop = previousScrollTop;
    }
  }

  function layoutMethodGrid() {
    if (!methodGridScroller) {
      return;
    }
    const top = methodGridScroller.getBoundingClientRect().top;
    const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
    const statusBar = document.getElementById('globalStatusBar');
    const statusTop = statusBar ? statusBar.getBoundingClientRect().top : viewportHeight;
    const bottomLimit = Math.min(viewportHeight, statusTop - 8);
    const available = Math.max(160, bottomLimit - top);
    methodGridScroller.style.height = String(available) + 'px';
  }

  function layoutMethodColumns() {
    if (!methodGrid || !methodGridCell) {
      return;
    }
    const tileWidth = 79;
    const gap = 4;
    const threeColWidth = tileWidth * 3 + gap * 2;
    const twoColWidth = tileWidth * 2 + gap;
    const oneColWidth = tileWidth;
    const scrollbarReserve = 14;

    const viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
    const imageWidth = planImage ? Math.ceil(planImage.getBoundingClientRect().width) : 0;
    const dialogMin = drawDialogCell ? Math.ceil(drawDialogCell.scrollWidth) : 0;
    const minRightWidth = Math.max(520, imageWidth, Math.min(dialogMin + 16, 760));
    const availableForLeft = Math.max(0, viewportWidth - minRightWidth - 32);

    let columns = 3;
    if (availableForLeft < threeColWidth) {
      columns = availableForLeft >= twoColWidth ? 2 : 1;
    }

    const selectedWidth = columns === 3 ? threeColWidth : (columns === 2 ? twoColWidth : oneColWidth);
    methodGrid.style.gridTemplateColumns = 'repeat(' + columns + ', ' + tileWidth + 'px)';
    const selectedCellWidth = selectedWidth + scrollbarReserve;
    methodGridCell.style.width = String(selectedCellWidth) + 'px';
    if (methodGridScroller) {
      methodGridScroller.style.width = String(selectedCellWidth) + 'px';
    }
  }

  function setStatus(msg) {
    statusMsg.textContent = msg || '';
  }

  function showError(msg) {
    if (msg) {
      errorBox.style.display = 'block';
      errorBox.textContent = 'Error: ' + msg;
    } else {
      errorBox.style.display = 'none';
      errorBox.textContent = '';
    }
  }

  function updateRefreshButtonVisibility() {
    if (!redrawBtn) {
      return;
    }
    redrawBtn.style.display = state.realtime ? 'none' : '';
  }

  function setMethodSwitchBusy(isBusy) {
    const gridButtons = methodGrid ? methodGrid.querySelectorAll('a, button') : [];
    gridButtons.forEach(function(node) {
      node.style.pointerEvents = isBusy ? 'none' : '';
      node.style.opacity = isBusy ? '0.6' : '';
    });

    if (redrawBtn) {
      redrawBtn.disabled = !!isBusy;
    }
    document.getElementById('randomBtn').disabled = !!isBusy;
    document.getElementById('defaultsBtn').disabled = !!isBusy;
    document.getElementById('drawBtn').disabled = !!isBusy;
    document.getElementById('playlistBtn').disabled = !!isBusy;
    document.getElementById('saveBtn').disabled = !!isBusy;
    document.getElementById('exportBtn').disabled = !!isBusy;
  }

  function startMethodSwitchBusy(requestId) {
    state.switchRequestId = requestId;
    if (state.switchBusyTimer) {
      clearTimeout(state.switchBusyTimer);
      state.switchBusyTimer = null;
    }
    setMethodSwitchBusy(true);
    // Safety release in case of lost websocket response
    state.switchBusyTimer = setTimeout(function() {
      state.switchBusyTimer = null;
      state.switchRequestId = null;
      setMethodSwitchBusy(false);
    }, 10000);
  }

  function endMethodSwitchBusy(requestId) {
    if (state.switchRequestId !== null && requestId !== state.switchRequestId) {
      return;
    }
    state.switchRequestId = null;
    if (state.switchBusyTimer) {
      clearTimeout(state.switchBusyTimer);
      state.switchBusyTimer = null;
    }
    setMethodSwitchBusy(false);
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

      const useSlider = !!field.slider && field.min !== undefined && field.min !== null && field.max !== undefined && field.max !== null;
      if (useSlider) {
        const wrapper = document.createElement('span');

        const slider = document.createElement('input');
        slider.type = 'range';
        slider.className = kind === 'DialogInt' ? 'intSlider' : 'floatSlider';
        slider.min = String(field.min);
        slider.max = String(field.max);
        slider.step = kind === 'DialogInt'
          ? '1'
          : String((field.step !== undefined && field.step !== null) ? field.step : 0.01);
        slider.dataset.fieldName = field.name;
        slider.dataset.sliderFor = field.name;

        input.value = value == null ? '' : String(value);
        slider.value = input.value === '' ? slider.min : input.value;

        input.addEventListener('input', function() {
          if (input.value !== '') {
            slider.value = input.value;
          }
        });
        slider.addEventListener('input', function() {
          input.value = slider.value;
        });

        wrapper.appendChild(input);
        wrapper.appendChild(slider);
        return wrapper;
      }
    } else {
      input.type = 'text';
    }

    input.value = value == null ? '' : String(value);
    if (kind === 'DialogStr' && field.length) {
      input.size = field.length;
    }
    return input;
  }

  function renderDialog() {
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
    layoutMethodColumns();
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

  function updateDialogValues() {
    state.fields.forEach(function(field) {
      if (!field.name || field.kind === 'DialogBreak') return;
      const node = dialogHost.querySelector('[data-field-name="' + field.name.replace(/"/g, '\\"') + '"]');
      if (!node) return;
      const sliderNode = dialogHost.querySelector('[data-slider-for="' + field.name.replace(/"/g, '\\"') + '"]');
      const value = Object.prototype.hasOwnProperty.call(state.params, field.name) ? state.params[field.name] : field.default;
      if (node.tagName === 'SELECT') {
        node.value = String(valueForChoiceField(field, value));
      } else if (field.kind === 'DialogColor' && Array.isArray(value) && value.length === 3) {
        const r = Number(value[0]).toString(16).padStart(2, '0');
        const g = Number(value[1]).toString(16).padStart(2, '0');
        const b = Number(value[2]).toString(16).padStart(2, '0');
        node.value = '#' + r + g + b;
      } else {
        node.value = value == null ? '' : String(value);
      }
      if (sliderNode) {
        sliderNode.value = node.value === '' ? sliderNode.min : node.value;
      }
    });
  }

  function _escapeHtml(str) {
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function applyPreviewData(data) {
    if (data.method) {
      state.method = data.method;
    }
    if (data.realtime !== undefined) {
      state.realtime = data.realtime !== false;
    }
    updateRefreshButtonVisibility();
    let methodsChanged = false;
    if (Array.isArray(data.methods)) {
      const nextMethods = data.methods;
      methodsChanged = nextMethods.length !== state.methods.length || nextMethods.some(function(m, idx) {
        return m !== state.methods[idx];
      });
      if (methodsChanged) {
        state.methods = nextMethods;
      }
    }
    const fieldsChanged = Array.isArray(data.fields);
    if (fieldsChanged) {
      state.fields = data.fields;
    }
    state.params = data.params || {};
    if (data.image && data.image.dataUrl) {
      planImage.src = data.image.dataUrl;
    } else if (data.image && data.image.url) {
      planImage.src = data.image.url;
    }
    const summary = data.summary || {};
    const isLong = (summary.seconds || 0) > 3600;
    if (summary.helpUrl) {
      const helpLink = '<a href="' + buildUrl('/' + summary.helpUrl) + '" target="_blank">Help!</a>';
      const timeHtml = summary.drawinfo ? (isLong ? '<span style="color:#cc0000;font-weight:bold;">' + _escapeHtml(summary.drawinfo) + '</span>' : _escapeHtml(summary.drawinfo)) : '';
      drawInfo.innerHTML = timeHtml + '&nbsp;&nbsp;&nbsp;&nbsp;<span class="navigation">' + helpLink + '</span>';
    } else {
      drawInfo.innerHTML = summary.drawinfo ? (isLong ? '<span style="color:#cc0000;font-weight:bold;">' + _escapeHtml(summary.drawinfo) + '</span>' : _escapeHtml(summary.drawinfo)) : '';
    }
    showError(data.errors || '');
    if (methodsChanged) {
      populateMethods(state.methods);
    } else {
      updateMethodSelection(state.method);
    }
    if (fieldsChanged) {
      renderDialog();
    } else {
      updateDialogValues();
    }
    // Keep shell-level state current so it survives page switches
    window.__sandtableDrawState = { method: state.method, params: state.params };
  }

  function _applySchema(data) {
    state.method = data.method;
    state.realtime = data.realtime !== false;
    updateRefreshButtonVisibility();
    state.fields = data.fields || [];
    state.params = {};
    state.fields.forEach(function(field) {
      if (field.name) {
        state.params[field.name] = field.default;
      }
    });
    window.history.replaceState(null, '', drawUrlForMethod(state.method));
    renderDialog();
  }

  const realtimePreview = (function() {
    let timer = null;
    const DELAY_MS = 250;
    return function() {
      if (!state.realtime) {
        return;
      }
      if (timer) {
        clearTimeout(timer);
      }
      timer = setTimeout(function() {
        timer = null;
        preview('refresh');
      }, DELAY_MS);
    };
  })();

  async function selectMethod(method) {
    setStatus('Loading method...');
    planImage.src = LOADING_SRC;
    try {
      state.method = method;
      window.history.replaceState(null, '', drawUrlForMethod(state.method));
      const requestId = preview('refresh', { includeFields: true, params: {} });
      startMethodSwitchBusy(requestId);
      updateMethodSelection(method);
    } catch (err) {
      showError(err.message || 'Method load failed');
      setStatus('');
      endMethodSwitchBusy(state.switchRequestId);
    }
  }

  // WebSocket-based interactive requests
  function preview(action, extraPayload) {
    const payload = Object.assign({
      method: state.method,
      action: action || 'refresh',
      params: collectParams(),
      requestId: state.latestPreviewRequestId + 1,
    }, extraPayload || {});

    const signature = JSON.stringify({
      method: payload.method,
      action: payload.action,
      params: payload.params,
      includeFields: !!payload.includeFields,
      includeImageData: !!payload.includeImageData,
      fieldName: payload.fieldName || '',
    });
    const now = Date.now();
    if (signature === state.lastPreviewSignature && (now - state.lastPreviewAt) < 350) {
      return;
    }
    state.lastPreviewSignature = signature;
    state.lastPreviewAt = now;

    setStatus('Working...');
    state.latestPreviewRequestId += 1;
    payload.requestId = state.latestPreviewRequestId;
    socket.emit('draw:preview', payload);
    return payload.requestId;
  }

  function randomizeField(fieldName) {
    preview('random-field', {fieldName: fieldName});
  }

  function restoreAllDefaults() {
    state.fields.forEach(function(field) {
      if (!field.name || field.kind === 'DialogBreak') return;
      const node = dialogHost.querySelector('[data-field-name="' + field.name.replace(/"/g, '\\"') + '"]');
      if (!node) return;
      const sliderNode = dialogHost.querySelector('[data-slider-for="' + field.name.replace(/"/g, '\\"') + '"]');
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
      if (sliderNode) {
        sliderNode.value = node.value === '' ? sliderNode.min : node.value;
      }
    });
    preview('refresh');
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
    const sliderNode = dialogHost.querySelector('[data-slider-for="' + fieldName.replace(/"/g, '\\"') + '"]');

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

    if (sliderNode) {
      sliderNode.value = node.value === '' ? sliderNode.min : node.value;
    }

    preview('refresh');
  }

  socket.on('draw:preview:response', function(data) {
    if (data && data.requestId && data.requestId !== state.latestPreviewRequestId) {
      return;
    }
    if (data.error) {
      showError(data.error);
      setStatus('');
      endMethodSwitchBusy(data && data.requestId);
    } else {
      applyPreviewData(data);
      setStatus('');
      endMethodSwitchBusy(data && data.requestId);
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
    if (data.error) {
      showError(data.error);
      setStatus('');
    } else if (data.status === 'ok') {
      if (data.image && data.image.dataUrl) {
        planImage.src = data.image.dataUrl;
      } else if (data.image && data.image.url) {
        planImage.src = data.image.url;
      }
      setStatus('Drawing...');
      showError('');
    }
  });

  socket.on('draw:complete', function() {
    setStatus('Draw complete');
  });

  function addToPlaylist() {
    setStatus('Adding to playlist...');
    socket.emit('draw:playlist:add', {
      method: state.method,
      params: collectParams(),
    });
  }

  socket.on('draw:playlist:add:response', function(data) {
    if (data && data.error) {
      showError(data.error);
      setStatus('');
      return;
    }
    const count = data && typeof data.count === 'number' ? data.count : null;
    setStatus(count === null ? 'Added to playlist' : ('Added to playlist (' + count + ' items)'));
    showError('');
  });

  function askForDrawingName(promptTitle) {
    const suggested = String(state.method || 'drawing').trim() || 'drawing';
    const entered = window.prompt(promptTitle, suggested);
    if (entered === null) {
      return '';
    }
    return String(entered).trim();
  }

  function saveDrawing() {
    const name = askForDrawingName('Save drawing as');
    if (!name) {
      return;
    }
    setStatus('Saving...');
    socket.emit('draw:save', {
      method: state.method,
      name: name,
      params: collectParams(),
    });
  }

  socket.on('draw:save:response', function(data) {
    if (data.error) {
      showError(data.error);
      setStatus('');
    } else if (data.status === 'ok') {
      setStatus('Saved');
      showError('');
    }
  });

  function exportDrawing() {
    const name = askForDrawingName('Export drawing as');
    if (!name) {
      return;
    }
    setStatus('Exporting...');
    socket.emit('draw:export', {
      method: state.method,
      name: name,
      params: collectParams(),
    });
  }

  socket.on('draw:export:response', function(data) {
    if (data.error) {
      showError(data.error);
      setStatus('');
    } else if (data.status === 'ok') {
      setStatus('Exported');
      showError('');
    }
  });

  // WebSocket connection handlers
  socket.on('connect', function() {
    setStatus('Connected');
  });

  socket.on('disconnect', function() {
    setStatus('Disconnected - attempting to reconnect');
  });

  socket.on('connect_error', function(error) {
    showError('Connection error: ' + error.message);
  });

  redrawBtn.addEventListener('click', function() {
    preview('refresh');
  });
  document.getElementById('randomBtn').addEventListener('click', function() {
    preview('random');
  });
  document.getElementById('defaultsBtn').addEventListener('click', restoreAllDefaults);
  document.getElementById('drawBtn').addEventListener('click', executeDraw);
  document.getElementById('playlistBtn').addEventListener('click', addToPlaylist);
  document.getElementById('saveBtn').addEventListener('click', saveDrawing);
  document.getElementById('exportBtn').addEventListener('click', exportDrawing);
  const onResize = function() {
    layoutMethodGrid();
    layoutMethodColumns();
  };
  window.addEventListener('resize', onResize);

  window.__sandtablePageCleanup = function() {
    window.removeEventListener('resize', onResize);
    if (socket && typeof socket.disconnect === 'function') {
      socket.disconnect();
    }
  };

  dialogHost.addEventListener('change', function(event) {
    if (event.target && event.target.dataset && event.target.dataset.fieldName) {
      realtimePreview();
    }
  });

  dialogHost.addEventListener('input', function(event) {
    if (!event.target || !event.target.dataset || !event.target.dataset.fieldName) {
      return;
    }
    var type = String(event.target.type || '').toLowerCase();
    if (type === 'range' || type === 'color') {
      realtimePreview();
    }
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
      layoutMethodGrid();
      layoutMethodColumns();
      updateRefreshButtonVisibility();
      populateMethods(state.methods);

      if (initialLoadname) {
        const loadData = await fetchJson(buildUrl('/api/draw/load'), {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({name: initialLoadname}),
        });
        if (loadData.method) {
          state.method = loadData.method;
        }
        if (loadData.realtime !== undefined) {
          state.realtime = loadData.realtime !== false;
        }
        applyPreviewData(loadData);
        window.history.replaceState(null, '', drawUrlForMethod(state.method));
      } else {
        if (_hasExplicitParams) {
          preview('refresh', { includeFields: true, params: initialParams });
        } else if (_savedDraw && _savedDraw.method) {
          preview('refresh', { includeFields: true, params: _savedDraw.params || {} });
        } else {
          preview('refresh', { includeFields: true, params: {} });
        }
      }

    } catch (err) {
      showError(err.message || 'Initialization failed');
      setStatus('Initialization failed');
    }
  })();
})();
</script>
