<table class="main">
 <tr>
  <form method="post" action="lights">
   <td valign="TOP">
    {% for pat in ledPatterns %}
      {% set style = 'ledselected' if pat == pattern else 'led' %}
      <button class="{{style}}" type="submit" name="method" value="{{pat}}">
       <img src="images/{{pat}}.png" width="100" height="80" alt="{{pat}}">
      </button>
      {% if loop.index0 % 3 == 2 %}
        <br>
      {% endif %}
    {% endfor %}
   </td>
  </form>

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

