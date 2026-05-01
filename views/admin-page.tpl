<div class="admingood" id="stats">
 <table>
 {% for row in statusRows %}
  <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td></tr>
 {% endfor %}
 </table>
</div>
<script>
if (typeof window.__sandtablePageCleanup === 'function') {
 try {
  window.__sandtablePageCleanup();
 } catch (err) {
  console.error(err);
 }
}
function updateStats(data,status) {
 stuff = data.stuff
 document.getElementById('stats').innerHTML = formatStuff(stuff);
}
function formatStuff(stuff) {
 text = '<table>\n';
 for (k of stuff) {
  text += '<tr><td>' + k[0] + '</td><td>' + k[1] + '</td></tr>';
 };
 text += '</table>';
 return( text );
}
var adminStatusSocket = window.__sandtableStatusSocket;
if (adminStatusSocket) {
 adminStatusSocket.on('admin:update', updateStats);
 adminStatusSocket.on('connect', function() {
  adminStatusSocket.emit('admin:subscribe');
 });
 if (adminStatusSocket.connected) {
  adminStatusSocket.emit('admin:subscribe');
 }
}
window.__sandtablePageCleanup = function() {
 if (adminStatusSocket) {
  adminStatusSocket.off('admin:update', updateStats);
 }
};
</script>

{% if message %}
 <div class="admingood">{{ message|safe }}</div>
 {% if message2 %}
  {{ message2|safe }}
 {% endif %}
{% else %}
 <div class="adminwarn">
  This is for SandTable administrative tasks.
 </div>
{% endif %}

<form method="post" action="admin">
 <fieldset>
  <legend>Preview Image Style</legend>
  {% for t in imageTypes %}
   <label><input type="radio" name="image_type" value="{{t}}"{% if t == imageType %} checked{% endif %}> {{t}}</label>
  {% endfor %}
  <button class="doit" name="action" type="submit" value="set_image_type">Set</button>
 </fieldset>
</form>

<form method="post" action="admin">
{% for k,v in actions|dictsort %}
 {% if v[1] %}
  <button class="doit" name="action" type="submit" value="{{k}}">{{v[1]}}</button><br>
 {% endif %}
{% endfor %}
</form>

