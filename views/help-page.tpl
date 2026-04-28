<html>
<head>
 <style>
{{ inline_css|safe }}
 </style>
 <title>Sand Table - Help</title>
</head>
    
<body>
<pre class="text">
{{ overview|safe }}
</pre>

<table class="help">
  {% for sand in sandables %}
    {% set sandable = makeSandable(sand) %}
    <tr><th class="help" colspan="3">{{sand}}</th></tr>
    {% for field in sandable.editor %}
      <tr>
        <td class="help">{{field.name}}</td>
        <td class="help">{{field.prompt}}</td>
        <td class="help">{{field.units}}</td>
      </tr>
    {% endfor %}
  {% endfor %}
</table>

</body>
</html>

