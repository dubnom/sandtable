<table class="main">
 <tr>
  <td valign="TOP">
   {% for sandy in sandables %}
    {% set style = 'selected' if sandy == sandable else 'sandable' %}
    <a href="draw?method={{sandy}}"><img src="images/{{sandy}}.png" width="75" height="60" class="{{style}}" alt="{{sandy}}"></a>
    {% if loop.index0 % 3 == 2 %}
     <br>
    {% endif %}
   {% endfor %}
  </td>
  <td valign="TOP">
   <center>
    <img class="plan" src="{{imagefile}}" width="{{width}}" height="{{height}}"><br>
    {% if errors %}
      <div class="error">Error: {{errors}}</div>
    {% endif %}
    {{ editor|safe }}
   </center>
  </td>
 </tr>
</table>
