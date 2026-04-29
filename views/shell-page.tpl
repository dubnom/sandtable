<html>
<head>
 <meta name="viewport" content="width=device-width, user-scalable=yes" />
 <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
 <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.3/jquery-ui.min.js"></script>
 <script src="//cdn.socket.io/4.5.4/socket.io.min.js"></script>
 <script>
  function randomInt(field, min, max) {
   number = min + Math.floor(Math.random() * (max - min));
   field.value = number;
  }
  function randomFloat(field, min, max) {
   number = min + Math.random() * (max - min);
   number = 0.0001 * Math.floor(number * 10000);
   field.value = number;
  }
 </script>
 <style>
{{ inline_css|safe }}
body {
 margin: 0;
 background-image: url("/images/sand_ripples.jpg");
}
#shellMenu {
 position: fixed;
 top: 0;
 left: 0;
 right: 0;
 z-index: 1001;
 padding: 8px 12px;
 background-color: rgba(0, 0, 0, 0.65);
 backdrop-filter: blur(4px);
}
#shellMenu .shellTitle {
 color: #f4f1de;
 font-size: 140%;
 margin-right: 14px;
}
#shellMenu .shellNav {
 display: flex;
 flex-wrap: wrap;
 gap: 6px;
 align-items: center;
}
#shellMenu .shellNav button {
 border-radius: 4px;
 border: 1px solid rgba(255,255,255,0.15);
 background-color: rgba(255,255,255,0.1);
 color: white;
 padding: 6px 10px;
 cursor: pointer;
}
#shellMenu .shellNav button.active {
 background-color: #dfbf00;
 color: black;
}
#shellContent {
 position: fixed;
 left: 0;
 right: 0;
 overflow: auto;
 padding: 8px;
}
#shellContentInner {
 min-height: 100%;
}
@media (max-width: 700px) {
 #shellMenu {
  padding: 6px 8px;
 }
 #shellMenu .shellTitle {
  display: block;
  margin-bottom: 6px;
  font-size: 120%;
 }
 #shellMenu .shellNav button {
  padding: 5px 8px;
  font-size: 90%;
 }
}
 </style>
 <title>Sand Table</title>
</head>
<body>
 <div id="shellMenu">
  <span class="shellTitle">Sand Table</span>
  <div class="shellNav">
   {% for label, path in menuItems %}
   <button type="button" data-view="{{ path }}"{% if path == initialView %} class="active"{% endif %}>{{ label }}</button>
   {% endfor %}
  </div>
 </div>
 <div id="shellContent">
  <div id="shellContentInner"></div>
 </div>
 {% include 'statusbar.tpl' %}
 <script>
 (function() {
  const menu = document.getElementById('shellMenu');
  const content = document.getElementById('shellContent');
  const contentInner = document.getElementById('shellContentInner');
  const buttons = Array.prototype.slice.call(document.querySelectorAll('#shellMenu [data-view]'));
  const bar = document.getElementById('globalStatusBar');
    let currentPath = '/{{ initialView }}';

  function normalizeView(view) {
   view = String(view || 'draw').replace(/^\/+/, '');
   const known = buttons.map(function(btn) { return btn.dataset.view; });
   return known.indexOf(view) >= 0 ? view : 'draw';
  }

  function extractView(path) {
   return normalizeView(String(path || '/draw').replace(/^\/+/, '').split('?')[0]);
  }

  function setActive(view) {
   buttons.forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.view === view);
   });
  }

    function initialPathFromLocation() {
     const shellUrl = new URL(window.location.href);
     const view = normalizeView(shellUrl.searchParams.get('view') || '{{ initialView }}');
     const passthrough = new URLSearchParams(shellUrl.search);
     passthrough.delete('view');
     const query = passthrough.toString();
     return '/' + view + (query ? ('?' + query) : '');
    }

  function layout() {
   const top = menu ? (menu.offsetHeight + 8) : 0;
   const bottom = bar ? (bar.offsetHeight + 16) : 90;
   content.style.top = String(top) + 'px';
   content.style.bottom = String(bottom) + 'px';
  }

  function disposeCurrentContent() {
   if (typeof window.__sandtablePageCleanup === 'function') {
    try {
     window.__sandtablePageCleanup();
    } catch (err) {
     console.error(err);
    }
   }
   window.__sandtablePageCleanup = null;
  }

  function executeScripts(root) {
   const scripts = Array.prototype.slice.call(root.querySelectorAll('script'));
   scripts.forEach(function(oldScript) {
    const script = document.createElement('script');
    Array.prototype.slice.call(oldScript.attributes).forEach(function(attr) {
     script.setAttribute(attr.name, attr.value);
    });
    script.text = oldScript.text || oldScript.textContent || oldScript.innerHTML || '';
    oldScript.parentNode.replaceChild(script, oldScript);
   });
  }

  function buildEmbedUrl(path) {
   const url = new URL(path, window.location.origin);
   url.searchParams.set('embed', '1');
   return url;
  }

  function normalizeTargetPath(path) {
   const url = new URL(path || '/', window.location.origin);
   if ((url.pathname === '/' || url.pathname === '') && url.searchParams.has('view')) {
    const view = normalizeView(url.searchParams.get('view'));
    const passthrough = new URLSearchParams(url.search);
    passthrough.delete('view');
    const query = passthrough.toString();
    return '/' + view + (query ? ('?' + query) : '');
   }
   return url.pathname + (url.search || '');
  }

  function cleanCurrentPath(url) {
   const cleaned = new URL(url.toString());
   cleaned.searchParams.delete('embed');
   return cleaned.pathname + (cleaned.search || '');
  }

  async function loadPath(path, push) {
    const normalizedPath = normalizeTargetPath(path || currentPath);
    const url = buildEmbedUrl(normalizedPath);
   const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {'X-Requested-With': 'XMLHttpRequest'}
   });
   const html = await response.text();
   if (!response.ok) {
    throw new Error('Failed to load ' + path);
   }

   window.__sandtableNextPath = normalizedPath;
   disposeCurrentContent();
   contentInner.innerHTML = html;
   executeScripts(contentInner);
   window.__sandtableNextPath = null;

   currentPath = cleanCurrentPath(url);
   const view = extractView(currentPath);
   setActive(view);
   if (push) {
    const shellUrl = new URL(window.location.href);
    shellUrl.searchParams.set('view', view);
    window.history.pushState({path: currentPath, view: view}, '', shellUrl.toString());
   }
   layout();
  }

  async function submitForm(form, push, submitter) {
   const method = String(form.getAttribute('method') || 'GET').toUpperCase();
   const action = form.getAttribute('action') || currentPath || '/' + extractView(currentPath);
   const normalizedAction = normalizeTargetPath(action);
   const url = buildEmbedUrl(normalizedAction);
   const options = {
    method: method,
    headers: {'X-Requested-With': 'XMLHttpRequest'}
   };
   const formData = new FormData(form);
   if (submitter && submitter.name) {
    formData.append(submitter.name, submitter.value || '');
   }

   if (method === 'GET') {
    const params = new URLSearchParams(formData);
    params.forEach(function(value, key) {
     url.searchParams.append(key, value);
    });
   } else {
    options.body = formData;
   }

   const response = await fetch(url.toString(), options);
   const html = await response.text();
   if (!response.ok) {
    throw new Error('Request failed');
   }

   window.__sandtableNextPath = cleanCurrentPath(url);
   disposeCurrentContent();
   contentInner.innerHTML = html;
   executeScripts(contentInner);
   window.__sandtableNextPath = null;

   currentPath = cleanCurrentPath(url);
   const view = extractView(currentPath);
   setActive(view);
   if (push) {
    const shellUrl = new URL(window.location.href);
    shellUrl.searchParams.set('view', view);
    window.history.pushState({path: currentPath, view: view}, '', shellUrl.toString());
   }
   layout();
  }

  buttons.forEach(function(btn) {
   btn.addEventListener('click', function() {
    loadPath('/' + btn.dataset.view, true).catch(function(err) {
     console.error(err);
    });
   });
  });

  content.addEventListener('click', function(event) {
   const link = event.target.closest('a[href]');
   if (!link) {
    return;
   }
   if (link.target && link.target !== '_self') {
    return;
   }
   const href = link.getAttribute('href');
   if (!href || href.startsWith('#') || href.startsWith('javascript:')) {
    return;
   }
   const url = new URL(href, window.location.origin);
   if (url.origin !== window.location.origin) {
    return;
   }
   event.preventDefault();
   loadPath(url.pathname + url.search, true).catch(function(err) {
    console.error(err);
   });
  });

  content.addEventListener('submit', function(event) {
   const form = event.target;
   if (!form || form.tagName !== 'FORM') {
    return;
   }
   event.preventDefault();
   submitForm(form, true, event.submitter || null).catch(function(err) {
    console.error(err);
   });
  });

  content.addEventListener('change', function(event) {
   const form = event.target.closest('form.auto_submit_form');
   if (!form) {
    return;
   }
   submitForm(form, true, null).catch(function(err) {
    console.error(err);
   });
  });

  window.addEventListener('resize', layout);
  window.addEventListener('popstate', function(event) {
   const path = event.state && event.state.path ? event.state.path : '/' + normalizeView(new URL(window.location.href).searchParams.get('view'));
   loadPath(path, false).catch(function(err) {
    console.error(err);
   });
  });

    currentPath = initialPathFromLocation();
    setActive(extractView(currentPath));
    layout();
    loadPath(currentPath, false).catch(function(err) {
   contentInner.innerHTML = '<div class="error">Error: ' + String(err.message || err) + '</div>';
  });
 })();
 </script>
</body>
</html>
