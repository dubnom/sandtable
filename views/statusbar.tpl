<style>
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
 <span class="statusbar-group"><strong>Machine:</strong> <span id="globalMachineStatus">Loading...</span></span>
 <span class="statusbar-group"><strong>Playlist:</strong> <span id="globalPlaylistStatus">Loading...</span></span>
 <button id="globalPlaylistPlayBtn" class="doit" type="button">Play</button>
 <button id="globalPlaylistStopBtn" class="load" type="button">Stop</button>
 <button id="globalPlaylistAbortBtn" class="abort" type="button">Abort</button>
</div>
<script>
(function() {
  const machineNode = document.getElementById('globalMachineStatus');
  const playlistNode = document.getElementById('globalPlaylistStatus');
  const playBtn = document.getElementById('globalPlaylistPlayBtn');
  const stopBtn = document.getElementById('globalPlaylistStopBtn');
  const abortBtn = document.getElementById('globalPlaylistAbortBtn');
  if (!machineNode || !playlistNode || !playBtn || !stopBtn || !abortBtn) {
    return;
  }

  const barNode = document.getElementById('globalStatusBar');

  if (typeof io === 'undefined') {
    machineNode.textContent = 'Unavailable';
    playlistNode.textContent = 'Socket.IO not loaded';
    playBtn.disabled = true;
    stopBtn.disabled = true;
    abortBtn.disabled = true;
    return;
  }

  const socket = window.__sandtableStatusSocket || io({reconnection: true});
  window.__sandtableStatusSocket = socket;

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
    const state = status.state || 'idle';
    const count = Number(status.count || 0);
    const current = status.current || null;
    let text = state;
    if (count) {
      text += ' (' + count + ' item' + (count === 1 ? '' : 's') + ')';
    }
    if (current && current.title) {
      text += ' - ' + current.title;
      if (status.currentIndex && status.total) {
        text += ' [' + status.currentIndex + '/' + status.total + ']';
      }
    } else if (status.message) {
      text += ' - ' + status.message;
    }
    return text;
  }

  function updateControls(status) {
    const state = status && status.state ? status.state : 'idle';
    const running = state === 'playing' || state === 'stopping' || state === 'aborting';
    playBtn.disabled = running || !status || !status.count;
    stopBtn.disabled = !running;
    abortBtn.disabled = !running;
  }

  function applyStatus(data) {
    machineNode.textContent = data && data.machine && data.machine.message ? data.machine.message : 'Unknown';
    playlistNode.textContent = describePlaylist(data ? data.playlist : null);
    updateControls(data ? data.playlist : null);
  }

  function controlPlaylist(action) {
    socket.emit('statusbar:control', {action: action});
  }

  socket.on('statusbar:update', function(data) {
    applyStatus(data);
    updateBodyPadding();
  });

  socket.on('statusbar:error', function(data) {
    const message = data && (data.message || data.error) ? (data.message || data.error) : 'Status update failed';
    playlistNode.textContent = message;
    updateControls(null);
  });

  socket.on('connect', function() {
    socket.emit('statusbar:subscribe');
  });

  socket.on('disconnect', function() {
    machineNode.textContent = 'Disconnected';
    playlistNode.textContent = 'Disconnected';
    updateControls(null);
    updateBodyPadding();
  });

  playBtn.addEventListener('click', function() { controlPlaylist('play'); });
  stopBtn.addEventListener('click', function() { controlPlaylist('stop'); });
  abortBtn.addEventListener('click', function() { controlPlaylist('abort'); });

  if (socket.connected) {
    socket.emit('statusbar:subscribe');
  }
})();
</script>
