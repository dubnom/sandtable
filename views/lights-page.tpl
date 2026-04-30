<form id="patternForm" method="post" action="lights">
  <input type="hidden" id="patternMethodInput" name="method" value="">
</form>
<table class="main">
 <tr>
   <td id="patternGridCell" valign="TOP" style="width: 330px;">
    <div id="patternGridScroller" style="overflow-y: scroll; overflow-x: hidden; overscroll-behavior: contain; scrollbar-gutter: stable; -webkit-overflow-scrolling: touch; width: fit-content; height: calc(100vh - 170px); min-height: 160px;">
      <div id="patternGrid" style="display: grid; grid-template-columns: repeat(3, 106px); gap: 4px;">
      {% for pat in ledPatterns %}
        {% set style = 'ledselected' if pat == pattern else 'led' %}
        <button class="{{style}}" type="button" data-pattern="{{pat}}">
         <img src="{{ patternImages.get(pat, 'images/' ~ pat ~ '.png') }}" width="100" height="80" alt="{{pat}}">
        </button>
      {% endfor %}
      </div>
    </div>
   </td>

  <td id="lightsDialogCell" valign="TOP">
   <center>
   <h3>{{pattern}}</h3>
   <form method="post" action="lights" class="auto_submit_form">
    <input name="method" type="hidden" value="{{pattern}}">
    {{ editor|safe }}
   </form>
   </center>
  </td>
 </tr>
</table>
<script>
(function() {
  var form = document.getElementById('patternForm');
  var methodInput = document.getElementById('patternMethodInput');
  var patternGrid = document.getElementById('patternGrid');
  var patternGridCell = document.getElementById('patternGridCell');
  var patternGridScroller = document.getElementById('patternGridScroller');
  var lightsDialogCell = document.getElementById('lightsDialogCell');

  function layoutPatternGrid() {
    if (!patternGridScroller) {
      return;
    }
    var top = patternGridScroller.getBoundingClientRect().top;
    var viewportHeight = window.innerHeight || document.documentElement.clientHeight || 0;
    var statusBar = document.getElementById('globalStatusBar');
    var statusTop = statusBar ? statusBar.getBoundingClientRect().top : viewportHeight;
    var bottomLimit = Math.min(viewportHeight, statusTop - 8);
    var available = Math.max(160, bottomLimit - top);
    patternGridScroller.style.height = String(available) + 'px';
  }

  function layoutPatternColumns() {
    if (!patternGrid || !patternGridCell) {
      return;
    }
    var tileWidth = 106;
    var gap = 4;
    var threeColWidth = tileWidth * 3 + gap * 2;
    var twoColWidth = tileWidth * 2 + gap;
    var oneColWidth = tileWidth;
    var scrollbarReserve = 14;

    var viewportWidth = window.innerWidth || document.documentElement.clientWidth || 0;
    var dialogMin = lightsDialogCell ? Math.ceil(lightsDialogCell.scrollWidth) : 0;
    var minRightWidth = Math.max(420, Math.min(dialogMin + 16, 760));
    var availableForLeft = Math.max(0, viewportWidth - minRightWidth - 32);

    var columns = 3;
    if (availableForLeft < threeColWidth) {
      columns = availableForLeft >= twoColWidth ? 2 : 1;
    }

    var selectedWidth = columns === 3 ? threeColWidth : (columns === 2 ? twoColWidth : oneColWidth);
    patternGrid.style.gridTemplateColumns = 'repeat(' + columns + ', ' + tileWidth + 'px)';
    var selectedCellWidth = selectedWidth + scrollbarReserve;
    patternGridCell.style.width = String(selectedCellWidth) + 'px';
    if (patternGridScroller) {
      patternGridScroller.style.width = String(selectedCellWidth) + 'px';
    }
  }

  window.addEventListener('resize', function() {
    layoutPatternGrid();
    layoutPatternColumns();
  });
  layoutPatternGrid();
  layoutPatternColumns();

  document.querySelectorAll('[data-pattern]').forEach(function(btn) {
    btn.addEventListener('click', function() {
      methodInput.value = btn.dataset.pattern;
      form.requestSubmit();
    });
  });
})();
</script>

