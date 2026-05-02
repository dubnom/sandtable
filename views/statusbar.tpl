<style>
#globalStatusBar {
 transition: background-color 0.15s ease, box-shadow 0.15s ease;
}

#globalStatusBar.statusbar-conn-reconnecting {
 box-shadow: 0 0 0 2px rgba(220, 136, 0, 0.45), 0 2px 10px rgba(0, 0, 0, 0.25);
}

#globalStatusBar.statusbar-conn-offline {
 box-shadow: 0 0 0 2px rgba(176, 0, 32, 0.45), 0 2px 10px rgba(0, 0, 0, 0.25);
}

#globalConnectionBadge {
 display: none;
 align-items: center;
 justify-content: center;
 min-width: 92px;
 padding: 2px 8px;
 border-radius: 999px;
 font-size: 78%;
 font-weight: bold;
 letter-spacing: 0.03em;
 text-transform: uppercase;
 background: #2e7d32;
 color: #fff;
}

#globalConnectionBadge.conn-reconnecting {
 background: #c77800;
}

#globalConnectionBadge.conn-offline {
 background: #b00020;
}

#globalStatusBar.statusbar-flash {
 background-color: rgba(255, 244, 173, 0.98) !important;
 box-shadow: 0 0 0 2px rgba(199, 161, 0, 0.45), 0 2px 10px rgba(0,0,0,0.25);
}

@media (max-width: 700px) {
 #globalStatusBar {
  left: 4px !important;
  right: 4px !important;
  bottom: 4px !important;
  padding: 6px 8px !important;
  gap: 6px !important;
  font-size: 85%;
 }

 #globalStatusBar button {
  margin: 0 !important;
  padding: 3px 8px;
  font-size: 90%;
 }

 #globalStatusBar .statusbar-group {
  flex-basis: 100%;
 }
}
</style>
<div id="globalStatusBar" style="position: fixed; left: 8px; right: 8px; bottom: 8px; margin: 0; padding: 8px 10px; background-color: rgba(255,255,255,0.92); border-radius: 6px; display: flex; flex-wrap: wrap; align-items: center; gap: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.25); z-index: 1000;">
 <span id="globalConnectionBadge" class="conn-online" aria-live="polite">Online</span>
 <span class="statusbar-group"><strong>Table:</strong> <span id="globalMachineStatus">Loading...</span></span>
 <span class="statusbar-group"><strong>Playlist:</strong> <span id="globalPlaylistStatus">Loading...</span></span>
 <button id="globalPlaylistPlayBtn" class="doit" type="button">Play</button>
 <button id="globalPlaylistStopBtn" class="load" type="button">Stop</button>
 <button id="globalReconnectBtn" type="button" style="display: none; color: #FFFFFF; background-color: #B00020;">Reconnect</button>
</div>
<script>
(function() {
  const pagePath = window.location.pathname || '/';
  const rootLikePath = pagePath.replace(/\/+$/, '');
  const appBasePath = rootLikePath === '' ? '' : rootLikePath;

  function buildUrl(path) {
    return (appBasePath ? appBasePath : '') + path;
  }

  const machineNode = document.getElementById('globalMachineStatus');
  const playlistNode = document.getElementById('globalPlaylistStatus');
  const playBtn = document.getElementById('globalPlaylistPlayBtn');
  const stopBtn = document.getElementById('globalPlaylistStopBtn');
  const reconnectBtn = document.getElementById('globalReconnectBtn');
  if (!machineNode || !playlistNode || !playBtn || !stopBtn || !reconnectBtn) {
    return;
  }

  const barNode = document.getElementById('globalStatusBar');
  const connectionBadgeNode = document.getElementById('globalConnectionBadge');
  let flashTimer = null;

  if (typeof io === 'undefined') {
    machineNode.textContent = 'Unavailable';
    playlistNode.textContent = 'Socket.IO not loaded';
    playBtn.disabled = true;
    stopBtn.disabled = true;
    stopBtn.style.display = 'none';
    reconnectBtn.style.display = '';
    return;
  }

  const socket = window.__sandtableStatusSocket || io({
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 10000,
    transports: ['websocket'],
    path: buildUrl('/socket.io')
  });
  window.__sandtableStatusSocket = socket;
  let reconnectAttempt = 0;

  function updateBodyPadding() {
    if (!barNode) {
      return;
    }
    document.body.style.paddingBottom = String(barNode.offsetHeight + 16) + 'px';
  }
  updateBodyPadding();
  window.addEventListener('resize', updateBodyPadding);

  function describePlaylist(status) {
    if (!status) {
      return 'Unavailable';
    }
    const playlistName = status.name ? String(status.name) : '';
    const state = status.state || 'idle';
    const count = Number(status.count || 0);
    const current = status.current || null;
    let text = playlistName ? (playlistName + ': ' + state) : state;
    if (count) {
      text += ' (' + count + ' item' + (count === 1 ? '' : 's') + ')';
    }
    if (current && status.currentIndex && status.total) {
      text += ' [' + status.currentIndex + '/' + status.total + ']';
    } else if (status.message) {
      text += ' - ' + status.message;
    }
    return text;
  }

  function formatDuration(seconds) {
    const total = Math.max(0, Number(seconds || 0));
    const whole = Math.round(total);
    const mins = Math.floor(whole / 60);
    const secs = whole % 60;
    const hours = Math.floor(mins / 60);
    const remMins = mins % 60;
    if (hours > 0) {
      return String(hours) + ':' + String(remMins).padStart(2, '0') + ':' + String(secs).padStart(2, '0');
    }
    return String(mins) + ':' + String(secs).padStart(2, '0');
  }

  function describeMachine(data) {
    const machine = data && data.machine ? data.machine : null;
    const drawing = data && data.drawing ? data.drawing : null;
    if (!machine) {
      return 'Unknown';
    }
    if (!drawing || drawing.state !== 'running') {
      return machine.message || 'Unknown';
    }

    const details = [];
    if (drawing.title) {
      details.push(drawing.title);
    } else if (drawing.method) {
      details.push(drawing.method);
    }
    if (drawing.percentComplete !== null && drawing.percentComplete !== undefined) {
      details.push(String(Math.round(Number(drawing.percentComplete))) + '%');
    }
    if (drawing.remainingSeconds) {
      details.push(formatDuration(drawing.remainingSeconds) + ' left');
    } else if (drawing.elapsedSeconds) {
      details.push('elapsed ' + formatDuration(drawing.elapsedSeconds));
    }
    return (machine.message || 'Busy') + ' - ' + details.join(' · ');
  }

  function updateControls(status) {
    const state = status && status.state ? status.state : 'idle';
    const running = state === 'playing' || state === 'stopping' || state === 'aborting';
    playBtn.disabled = running || !status || !status.count;
    stopBtn.disabled = !running;
    playBtn.style.display = running ? 'none' : '';
    stopBtn.style.display = running ? '' : 'none';
  }

  function flashStatusBar() {
    if (!barNode) {
      return;
    }
    if (flashTimer !== null) {
      window.clearTimeout(flashTimer);
    }
    barNode.classList.remove('statusbar-flash');
    void barNode.offsetWidth;
    barNode.classList.add('statusbar-flash');
    flashTimer = window.setTimeout(function() {
      barNode.classList.remove('statusbar-flash');
      flashTimer = null;
    }, 500);
  }

  function captureDisplayedState() {
    return {
      machine: machineNode.textContent,
      playlist: playlistNode.textContent,
      playDisabled: playBtn.disabled,
      stopDisabled: stopBtn.disabled,
      reconnectVisible: reconnectBtn.style.display !== 'none'
    };
  }

  function maybeFlashStatusBar(beforeState) {
    const afterState = captureDisplayedState();
    if (
      beforeState.machine !== afterState.machine ||
      beforeState.playlist !== afterState.playlist ||
      beforeState.playDisabled !== afterState.playDisabled ||
      beforeState.stopDisabled !== afterState.stopDisabled ||
      beforeState.reconnectVisible !== afterState.reconnectVisible
    ) {
      flashStatusBar();
    }
  }

  function applyStatus(data) {
    const beforeState = captureDisplayedState();
    machineNode.textContent = describeMachine(data);
    playlistNode.textContent = describePlaylist(data ? data.playlist : null);
    updateControls(data ? data.playlist : null);
    maybeFlashStatusBar(beforeState);
  }

  function controlPlaylist(action) {
    socket.emit('statusbar:control', {action: action});
  }

  function setReconnectVisible(visible) {
    reconnectBtn.style.display = visible ? '' : 'none';
  }

  function setConnectionState(mode) {
    if (!connectionBadgeNode || !barNode) {
      return;
    }
    connectionBadgeNode.classList.remove('conn-online', 'conn-reconnecting', 'conn-offline');
    barNode.classList.remove('statusbar-conn-reconnecting', 'statusbar-conn-offline');
    connectionBadgeNode.style.display = 'none';

    if (mode === 'offline') {
      connectionBadgeNode.classList.add('conn-offline');
      connectionBadgeNode.textContent = 'Offline';
      connectionBadgeNode.style.display = 'inline-flex';
      barNode.classList.add('statusbar-conn-offline');
      return;
    }
    if (mode === 'reconnecting') {
      barNode.classList.add('statusbar-conn-reconnecting');
      return;
    }
  }

  function reconnectMessage(prefix) {
    if (reconnectAttempt <= 0) {
      return prefix;
    }
    return prefix + ' (attempt ' + reconnectAttempt + ')';
  }

  socket.on('statusbar:update', function(data) {
    applyStatus(data);
    updateBodyPadding();
  });

  socket.on('statusbar:error', function(data) {
    const beforeState = captureDisplayedState();
    const message = data && (data.message || data.error) ? (data.message || data.error) : 'Status update failed';
    playlistNode.textContent = message;
    updateControls(null);
    maybeFlashStatusBar(beforeState);
  });

  socket.on('connect', function() {
    reconnectAttempt = 0;
    setConnectionState('online');
    setReconnectVisible(false);
    reconnectBtn.disabled = false;
    socket.emit('statusbar:subscribe');

    // Refresh once on connect/reconnect in case an update event was missed.
    fetch(buildUrl('/api/statusbar'), {credentials: 'same-origin'})
      .then(function(response) { return response.json(); })
      .then(function(snapshot) { applyStatus(snapshot); updateBodyPadding(); })
      .catch(function() {});
  });

  socket.on('disconnect', function() {
    const beforeState = captureDisplayedState();
    setConnectionState('reconnecting');
    machineNode.textContent = 'Disconnected';
    playlistNode.textContent = reconnectMessage('Disconnected - reconnecting');
    updateControls(null);
    setReconnectVisible(true);
    maybeFlashStatusBar(beforeState);
    updateBodyPadding();
  });

  socket.on('reconnect_attempt', function(attempt) {
    reconnectAttempt = Number(attempt || (reconnectAttempt + 1));
    const beforeState = captureDisplayedState();
    setConnectionState('reconnecting');
    machineNode.textContent = 'Disconnected';
    playlistNode.textContent = reconnectMessage('Reconnecting');
    setReconnectVisible(true);
    maybeFlashStatusBar(beforeState);
    updateBodyPadding();
  });

  socket.on('reconnect_error', function() {
    const beforeState = captureDisplayedState();
    setConnectionState('reconnecting');
    playlistNode.textContent = reconnectMessage('Reconnect error');
    setReconnectVisible(true);
    maybeFlashStatusBar(beforeState);
    updateBodyPadding();
  });

  socket.on('reconnect_failed', function() {
    const beforeState = captureDisplayedState();
    setConnectionState('offline');
    playlistNode.textContent = reconnectMessage('Reconnect failed');
    setReconnectVisible(true);
    reconnectBtn.disabled = false;
    maybeFlashStatusBar(beforeState);
    updateBodyPadding();
  });

  playBtn.addEventListener('click', function() { controlPlaylist('play'); });
  stopBtn.addEventListener('click', function() { controlPlaylist('stop'); });
  reconnectBtn.addEventListener('click', function() {
    reconnectBtn.disabled = true;
    const beforeState = captureDisplayedState();
    setConnectionState('reconnecting');
    playlistNode.textContent = 'Manual reconnect requested';
    maybeFlashStatusBar(beforeState);
    try {
      if (!socket.connected) {
        socket.connect();
      } else {
        socket.emit('statusbar:subscribe');
      }
    } catch (err) {
      window.location.reload();
      return;
    }
    window.setTimeout(function() {
      reconnectBtn.disabled = false;
      if (!socket.connected) {
        window.location.reload();
      }
    }, 4000);
  });

  if (socket.connected) {
    setConnectionState('online');
    setReconnectVisible(false);
    socket.emit('statusbar:subscribe');
  } else {
    setConnectionState('offline');
    setReconnectVisible(true);
    stopBtn.style.display = 'none';
  }
})();
</script>
