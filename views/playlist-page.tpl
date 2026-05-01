<div class="historybox">
 <br>

 <form method="post" action="playlist" class="savebox" style="margin-bottom: 12px;">
   <span class="save">Playlists</span>
   <select class="load" id="playlistSelect" name="_loadname">
   {% if savedPlaylists and savedPlaylists|length %}
    {% for name in savedPlaylists %}
     <option value="{{ name }}"{% if name == selectedSaved %} selected{% endif %}>{{ name }}</option>
    {% endfor %}
   {% else %}
    <option value="">(none)</option>
   {% endif %}
  </select>
   <input type="hidden" id="playlistAction" name="action" value="load">
   <input type="hidden" id="playlistName" name="_name" value="">
  <button class="save" id="playlistSaveAsBtn" type="button">Save As...</button>
 </form>
 <script>
 (function() {
   var selectedSaved = {{ selectedSaved|tojson }};
   var select = document.getElementById('playlistSelect');
   var form = select ? select.form : null;
   var actionInput = document.getElementById('playlistAction');
   var nameInput = document.getElementById('playlistName');
   var saveAsBtn = document.getElementById('playlistSaveAsBtn');
   if (!select || !form || !actionInput || !nameInput || !saveAsBtn) {
    return;
   }
   select.addEventListener('change', function() {
    actionInput.value = 'load';
    form.requestSubmit();
   });

   saveAsBtn.addEventListener('click', function() {
    var suggested = String(select.value || selectedSaved || 'Untitled');
    var entered = prompt('Save playlist as', suggested);
    if (entered === null) {
     return;
    }
    entered = String(entered).trim();
    if (!entered) {
      return;
    }
    nameInput.value = entered;
    actionInput.value = 'save';
    form.requestSubmit();
   });

   function playlistIsActive(status) {
    var playlist = status && status.playlist ? status.playlist : null;
    var playlistState = playlist && playlist.state ? String(playlist.state) : '';
    return playlistState === 'playing' || playlistState === 'stopping' || playlistState === 'aborting';
   }

   function fetchStatusSnapshot() {
    return fetch('/api/statusbar', {
      credentials: 'same-origin'
    }).then(function(response) {
      if (!response.ok) {
        throw new Error('Unable to check machine status');
      }
      return response.json();
    });
   }

   function abortBusyMachine(status) {
    var url = playlistIsActive(status) ? '/api/statusbar/control' : '/api/draw/abort';
    var payload = playlistIsActive(status) ? {action: 'abort'} : {};
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'same-origin',
      body: JSON.stringify(payload)
    }).then(function(response) {
      return response.json().catch(function() {
        return {};
      }).then(function(data) {
        if (!response.ok || (data && data.status === 'error')) {
          throw new Error((data && (data.message || data.error)) || 'Unable to abort current job');
        }
        return data;
      });
    });
   }

   function guardBusyDrawSubmission(event) {
    var target = event.target;
    if (!target || !target.matches('form[action="playlist"]')) {
      return;
    }

    var actionField = target.querySelector('input[name="action"]');
    var action = actionField ? String(actionField.value || '').toLowerCase() : '';
    if (action !== 'draw' && action !== 'drawall') {
      return;
    }

    event.preventDefault();
    fetchStatusSnapshot().then(function(status) {
      if (status && status.machine && status.machine.ready) {
        target.submit();
        return;
      }

      var label = action === 'drawall' ? 'draw playlist' : 'draw';
      if (!window.confirm('Machine is busy. Confirm abort and ' + label + '?')) {
        return;
      }

      return abortBusyMachine(status).then(function() {
        target.submit();
      });
    }).catch(function(error) {
      window.alert(error && error.message ? error.message : 'Unable to check machine status');
    });
   }

   document.addEventListener('submit', guardBusyDrawSubmission, true);
 })();
 </script>

 {% if status %}
    <div class="status">{{ status }}</div><br>
 {% endif %}
 {% if error %}
    <div class="error">Error: {{ error }}</div><br>
 {% endif %}

 {% if items and items|length %}
  <form method="post" action="playlist" style="margin-bottom: 12px;">
     <button class="doit" type="submit" name="action" value="drawall">Draw Playlist</button>
    <button class="delete" type="submit" name="action" value="clear" style="font-size: 100%; margin: 3px 3px 3px 3px; padding: 2px 6px;" onclick="return confirm('Clear the entire playlist?');">Clear Playlist</button>
  </form>

  <table class="help" cellspacing="0" cellpadding="4" style="background-color: rgba(255,255,255,0.85);">
   <tr>
      <th class="help">Image</th>
    <th class="help">Title</th>
    <th class="help">Method</th>
    <th class="help">Added</th>
    <th class="help">Actions</th>
   </tr>
   {% for item in items %}
   <tr>
      <td class="help">
       {% if item.imageUrl %}
              <a href="/?view=draw&method={{ item.method }}&playlistItemId={{ item.id }}" title="Open in Draw">
          <img src="{{ item.imageUrl }}" alt="{{ item.title }}" width="96" class="history" style="height: auto;">
              </a>
       {% endif %}
      </td>
    <td class="help">{{ item.title }}</td>
      <td class="help"><a href="/draw?method={{ item.method }}">{{ item.method }}</a></td>
        <td class="help">{{ item.createdText }}</td>
    <td class="help">
    <form method="post" action="playlist" style="display:inline;">
     <input type="hidden" name="action" value="moveup">
     <input type="hidden" name="id" value="{{ item.id }}">
      <button class="load" type="submit"{% if loop.first %} disabled{% endif %}>&uarr;</button>
    </form>
    <form method="post" action="playlist" style="display:inline;">
     <input type="hidden" name="action" value="movedown">
     <input type="hidden" name="id" value="{{ item.id }}">
      <button class="load" type="submit"{% if loop.last %} disabled{% endif %}>&darr;</button>
    </form>
        <form method="post" action="playlist" style="display:inline;">
         <input type="hidden" name="action" value="draw">
         <input type="hidden" name="id" value="{{ item.id }}">
         <button class="doit" type="submit">Draw</button>
        </form>
     <form method="post" action="playlist" style="display:inline;">
      <input type="hidden" name="action" value="remove">
      <input type="hidden" name="id" value="{{ item.id }}">
      <button class="delete" type="submit">Remove</button>
     </form>
    </td>
   </tr>
   {% endfor %}
  </table>
 {% else %}
  <span class="navigation">Playlist is empty.</span>
 {% endif %}
</div>
