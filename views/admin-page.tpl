<div class="admingood" id="stats">STATS</div>
<script>
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
setInterval(updater, 2500);
</script>

%if message:
 <div class="admingood">{{!message}}</div>
 %if message2:
  {{!message2}}
 %end
%else:
 <div class="adminwarn">
  This is for SandTable administrative tasks.
 </div>
%end

<form method="post" action="admin">
%for k,v in iter(sorted(actions.items())):
 %if v[1]:
  <button class="doit" name="action" type="submit" value="{{k}}">{{v[1]}}</button><br>
 %end
%end
</form>

