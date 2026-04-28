<div class="admingood" id="stats">STATS</div>
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
function updater() {
 $.post("admin/status", {}, updateStats);
} 
updater();
var adminStatsInterval = setInterval(updater, 2500);
window.__sandtablePageCleanup = function() {
 clearInterval(adminStatsInterval);
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
{% for k,v in actions|dictsort %}
 {% if v[1] %}
  <button class="doit" name="action" type="submit" value="{{k}}">{{v[1]}}</button><br>
 {% endif %}
{% endfor %}
</form>

