<table class="main">
 <tr>
  <td valign="TOP" style="width: 230px;">
   <div class="navigation" style="margin-bottom: 8px;">Method</div>
     <div id="methodGrid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px;"></div>
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
     <button id="abortBtn" class="abort" type="button">Abort!</button>
    </div>
    <div class="savebox" style="margin-top: 10px;">
     <span class="save">Name</span>
     <input id="nameInput" class="save" type="text" size="24">
     <button id="saveBtn" class="save" type="button">Save</button>
     <button id="exportBtn" class="export" type="button">Export</button>
    </div>
   </center>
  </td>
 </tr>
</table>

<script src="//cdn.socket.io/4.5.4/socket.io.min.js"></script>
<script>
(function() {
  const initialMethod = {{ method|tojson }};
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

  const state = {
    method: initialMethod,
    methods: fallbackMethods || [],
    fields: [],
    params: {},
    realtime: true,
  };

  const methodGrid = document.getElementById('methodGrid');
  const planImage = document.getElementById('planImage');
  const errorBox = document.getElementById('errorBox');
  const drawInfo = document.getElementById('drawInfo');
  const dialogHost = document.getElementById('dialogHost');
  const statusMsg = document.getElementById('statusMsg');
  const nameInput = document.getElementById('nameInput');

  function methodImageUrl(method) {
    return buildUrl('/images/' + encodeURIComponent(method) + '.png');
  }

  function populateMethods(methods) {
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
      choices.forEach(function(choice) {
        const opt = document.createElement('option');
        opt.value = String(choice);
        opt.textContent = String(choice);
        if (String(choice) === String(value)) {
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
    if (data.method) {
      state.method = data.method;
    }
    if (Array.isArray(data.fields)) {
      state.fields = data.fields;
    }
    state.params = data.params || {};
    if (data.image && data.image.dataUrl) {
      planImage.src = data.image.dataUrl;
    } else if (data.image && data.image.url) {
      planImage.src = data.image.url;
    }
    const summary = data.summary || {};
    drawInfo.textContent = summary.drawinfo || '';
    showError(data.errors || '');
    populateMethods(state.methods);
    renderDialog();
  }

  async function loadMethods() {
    const data = await fetchJson(buildUrl('/api/draw/methods?method=' + encodeURIComponent(state.method)));
    state.methods = data.methods || [];
    populateMethods(state.methods);
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
        window.history.replaceState(null, '', drawUrlForMethod(state.method));
        renderDialog();
        resolve(data);
      });

      socket.emit('draw:schema', {method: method});
    });
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
    try {
      await loadSchema(method);
      await preview('refresh');
      populateMethods(state.methods);
    } catch (err) {
      showError(err.message || 'Method load failed');
      setStatus('');
    }
  }

  // WebSocket-based interactive requests
  function preview(action) {
    setStatus('Working...');
    socket.emit('draw:preview', {
      method: state.method,
      action: action || 'refresh',
      params: collectParams(),
    });
  }

  socket.on('draw:preview:response', function(data) {
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

  function abortDraw() {
    setStatus('Stopping...');
    socket.emit('draw:abort', {});
  }

  socket.on('draw:abort:response', function(data) {
    if (data.error) {
      showError(data.error);
    } else {
      setStatus('Stopped');
      showError('');
    }
  });

  function saveDrawing() {
    setStatus('Saving...');
    socket.emit('draw:save', {
      method: state.method,
      name: nameInput.value || '',
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
    setStatus('Exporting...');
    socket.emit('draw:export', {
      method: state.method,
      name: nameInput.value || '',
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

  document.getElementById('redrawBtn').addEventListener('click', function() {
    preview('refresh');
  });
  document.getElementById('randomBtn').addEventListener('click', function() {
    preview('random');
  });
  document.getElementById('drawBtn').addEventListener('click', executeDraw);
  document.getElementById('abortBtn').addEventListener('click', abortDraw);
  document.getElementById('saveBtn').addEventListener('click', saveDrawing);
  document.getElementById('exportBtn').addEventListener('click', exportDrawing);

  dialogHost.addEventListener('change', function(event) {
    if (event.target && event.target.dataset && event.target.dataset.fieldName) {
      realtimePreview();
    }
  });

  dialogHost.addEventListener('input', function(event) {
    if (event.target && event.target.dataset && event.target.dataset.fieldName) {
      realtimePreview();
    }
  });

  (async function init() {
    try {
      // Always show a method list immediately, even if API calls fail.
      populateMethods(state.methods);

      try {
        await loadMethods();
      } catch (err) {
        setStatus('Using built-in method list');
      }

      await loadSchema(state.method);
      await preview('refresh');
    } catch (err) {
      showError(err.message || 'Initialization failed');
      setStatus('Initialization failed');
    }
  })();
})();
</script>
