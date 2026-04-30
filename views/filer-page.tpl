<script>
var FILER_STATE_KEY = '__sandtableFilerState';
var FILER_RESTORE_FLAG_KEY = '__sandtableFilerShouldRestore';
var FILER_ACTIONS_VISIBLE_KEY = '__sandtableFilerActionsVisible';

function filerActionsVisible() {
  return window[FILER_ACTIONS_VISIBLE_KEY] === true;
}

function filerApplyActionsVisibility(visible) {
  var filesForm = document.getElementById('files');
  if (!filesForm) {
    return;
  }
  if (visible) {
    filesForm.classList.remove('filer-actions-hidden');
  } else {
    filesForm.classList.add('filer-actions-hidden');
  }
  window[FILER_ACTIONS_VISIBLE_KEY] = !!visible;
  var button = document.getElementById('toggleFileActions');
  if (button) {
    button.textContent = visible ? 'Hide Actions' : 'Show Actions';
  }
}

function filerToggleActions() {
  filerApplyActionsVisibility(!filerActionsVisible());
}

function myDelete(nm,fn,ft) {
  var deleted = confirm( "Permanently delete " + nm + "?" );
  if (deleted == true) {
    $.post("filer/delete", { nm: nm, filename: fn, ft: ft }, function(data,status) {
      if (data.result) {
        document.getElementById(fn).innerHTML = '<span class="filername">' + data.text + '</span>'; }
      else {
        alert( data.text ); }
    });
  }
}
function myRename(nm,fn,ft) {
  var newName = prompt( "Rename " + nm, nm);
  if (newName != null) {
    $.post("filer/rename", {nm: nm,  oldname: fn, newname: newName, ft: ft }, function(data,status) {
      if (data.result) {
        document.getElementById(fn).innerHTML = '<span class="filername">' + data.text + '</span>'; }
      else {
        alert( data.text ); }
    });
  }
}
function mySubmit(action,name,value,name2,value2) {
  if (action === 'draw' && name === 'action' && value.toLowerCase() === 'load' && name2 === '_loadname') {
    window.location.href = '/?view=draw&loadname=' + encodeURIComponent(value2);
    return;
  }
  $('<input />').attr('type','hidden').attr('name',name).attr('value',value).appendTo('#files');
  $('<input />').attr('type','hidden').attr('name',name2).attr('value',value2).appendTo('#files');
  document.getElementById('files').action = action;
  document.getElementById('files').submit();
}

function filerSetState(filetype, directory) {
  window[FILER_STATE_KEY] = {
    filetype: String(filetype || ''),
    directory: String(directory || '')
  };
}

function filerRestoreStateIfNeeded() {
  const saved = window[FILER_STATE_KEY];
  const shouldRestore = !!window[FILER_RESTORE_FLAG_KEY];
  if (!saved || typeof saved !== 'object') {
    filerSetState({{ ft|tojson }}, {{ path|tojson }});
    return;
  }
  const currentFiletype = {{ ft|tojson }};
  const currentDirectory = {{ path|tojson }};
  const targetFiletype = typeof saved.filetype === 'string' ? saved.filetype : '';
  const targetDirectory = typeof saved.directory === 'string' ? saved.directory : '';
  if (!shouldRestore || !targetFiletype || (targetFiletype === currentFiletype && targetDirectory === currentDirectory)) {
    window[FILER_RESTORE_FLAG_KEY] = false;
    filerSetState(currentFiletype, currentDirectory);
    return;
  }

  window[FILER_RESTORE_FLAG_KEY] = false;
  const data = new FormData();
  data.append('filetype', targetFiletype);
  if (targetDirectory) {
    data.append('directory', targetDirectory);
  }

  fetch('/filer?embed=1', {
    method: 'POST',
    body: data,
    headers: {'X-Requested-With': 'XMLHttpRequest'}
  }).then(function(response) {
    return response.text();
  }).then(function(html) {
    const contentInner = document.getElementById('shellContentInner');
    if (!contentInner) {
      return;
    }
    // Clear cleanup before re-injecting so new scripts take the first (non-chaining) branch
    window.__sandtablePageCleanup = null;
    contentInner.innerHTML = html;
    const scripts = Array.prototype.slice.call(contentInner.querySelectorAll('script'));
    scripts.forEach(function(oldScript) {
      const script = document.createElement('script');
      Array.prototype.slice.call(oldScript.attributes).forEach(function(attr) {
        script.setAttribute(attr.name, attr.value);
      });
      script.text = oldScript.text || oldScript.textContent || oldScript.innerHTML || '';
      oldScript.parentNode.replaceChild(script, oldScript);
    });
  }).catch(function(err) {
    console.error(err);
  });
}

if (typeof window.__sandtablePageCleanup !== 'function') {
  window.__sandtablePageCleanup = function() {
    const nextPath = String(window.__sandtableNextPath || '');
    if (nextPath.startsWith('/filer')) {
      return;
    }
    filerSetState({{ ft|tojson }}, {{ path|tojson }});
    window[FILER_RESTORE_FLAG_KEY] = true;
  };
}

filerRestoreStateIfNeeded();

if (!window.__sandtableFilerListenersBound) {
  document.addEventListener('click', function(event) {
    const button = event.target.closest('#toggleFileActions');
    if (button) {
      filerToggleActions();
      return;
    }

    const filesForm = document.getElementById('files');
    if (!filesForm) {
      return;
    }
    const dirButton = event.target.closest('button[name="directory"]');
    if (!dirButton || !filesForm.contains(dirButton)) {
      return;
    }
    const filetypeInput = filesForm.querySelector('input[name="filetype"]');
    const currentFiletype = filetypeInput ? String(filetypeInput.value || '') : '';
    filerSetState(currentFiletype, String(dirButton.value || ''));
  });

  document.addEventListener('change', function(event) {
    const select = event.target;
    if (!select || select.name !== 'filetype') {
      return;
    }
    filerSetState(String(select.value || ''), '');
  });

  window.__sandtableFilerListenersBound = true;
}
</script>

<style>
#files.filer-actions-hidden .filer-actions {
  display: none;
}
</style>

<form method="post" action="/filer" class="auto_submit_form">
 <div class="filerbox">
  <select class="filer" name="filetype">
   {{ options|safe }}
  </select>
 </div>
</form>

{% if upload %}
 <form id="uploadForm" enctype="multipart/form-data" method="post" action="/filer">
  <div class="savebox">
   <input type="hidden" name="filetype" value="{{ft}}"/>
   <input type="hidden" name="directory" value="{{path}}"/>
   <input id="uploadInput" class="upload" name="_file" type="file" accept="{{ftfilter}}" required multiple/>
   <button class="upload" name="action" type="submit" value="upload">Upload</Button>
  </div>
  <div id="uploadDropZone" class="savebox" style="margin-top: 8px; border: 2px dashed #888; border-radius: 6px; padding: 10px; text-align: center;">
   Drag and drop files here to upload
  </div>
 </form>
 <script>
 (function() {
  const form = document.getElementById('uploadForm');
  const input = document.getElementById('uploadInput');
  const zone = document.getElementById('uploadDropZone');
  if (!form || !input || !zone) {
   return;
  }

  function uploadFiles(fileList) {
   if (!fileList || !fileList.length) {
    return;
   }
   const data = new FormData();
   data.append('filetype', '{{ft}}');
   data.append('directory', '{{path}}');
   data.append('action', 'upload');
   for (let i = 0; i < fileList.length; i += 1) {
    data.append('_file', fileList[i]);
   }

   fetch('/filer?embed=1', {
    method: 'POST',
    body: data,
    headers: {'X-Requested-With': 'XMLHttpRequest'}
   }).then(function(response) {
    return response.text();
   }).then(function(html) {
    const contentInner = document.getElementById('shellContentInner');
    if (contentInner) {
     contentInner.innerHTML = html;
     const scripts = Array.prototype.slice.call(contentInner.querySelectorAll('script'));
     scripts.forEach(function(oldScript) {
      const script = document.createElement('script');
      Array.prototype.slice.call(oldScript.attributes).forEach(function(attr) {
       script.setAttribute(attr.name, attr.value);
      });
      script.text = oldScript.text || oldScript.textContent || oldScript.innerHTML || '';
      oldScript.parentNode.replaceChild(script, oldScript);
     });
    }
   }).catch(function(err) {
    console.error(err);
   });
  }

  zone.addEventListener('dragover', function(event) {
   event.preventDefault();
   zone.style.borderColor = '#dfbf00';
  });

  zone.addEventListener('dragleave', function(event) {
   event.preventDefault();
   zone.style.borderColor = '#888';
  });

  zone.addEventListener('drop', function(event) {
   event.preventDefault();
   zone.style.borderColor = '#888';
   uploadFiles(event.dataTransfer && event.dataTransfer.files ? event.dataTransfer.files : null);
  });

  input.addEventListener('change', function() {
   uploadFiles(input.files);
  });
 })();
 </script>
{% endif %}

<form id="files" method="post" action="filer">
 <input type="hidden" name="filetype" value="{{ft}}"/>
 <span class="filerTitle">{{path}}</span>
 <button id="toggleFileActions" class="load" type="button" style="margin-left: 8px;">Show Actions</button>
 <table id="filetable">
  {{ table|safe }}
 </table>
</form>

<script>
filerApplyActionsVisibility(filerActionsVisible());
</script>
