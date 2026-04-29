<form id="patternForm" method="post" action="lights">
  <input type="hidden" id="patternMethodInput" name="method" value="">
</form>
<table class="main">
 <tr>
   <td valign="TOP">
    {% for pat in ledPatterns %}
      {% set style = 'ledselected' if pat == pattern else 'led' %}
      <button class="{{style}}" type="button" data-pattern="{{pat}}">
       <img src="{{ patternImages.get(pat, 'images/' ~ pat ~ '.png') }}" width="100" height="80" alt="{{pat}}">
      </button>
      {% if loop.index0 % 3 == 2 %}
        <br>
      {% endif %}
    {% endfor %}
   </td>

  <td valign="TOP">
   <center>
   <h3>{{pattern}}</h3>
   <form method="post" action="lights" class="auto_submit_form">
    <input name="method" type="hidden" value="{{pattern}}">
    {{ editor|safe }}
    <button class="doit" name="action" type="submit" value="doit">Lights!</button>
   </form>
   </center>
  </td>
 </tr>
</table>
<script>
(function() {
  var form = document.getElementById('patternForm');
  var methodInput = document.getElementById('patternMethodInput');
  document.querySelectorAll('[data-pattern]').forEach(function(btn) {
    btn.addEventListener('click', function() {
      methodInput.value = btn.dataset.pattern;
      form.requestSubmit();
    });
  });
})();
</script>

