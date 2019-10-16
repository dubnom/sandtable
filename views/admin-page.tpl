<div class="admingood" id="stats">STATS</div>
<script>
function updateStats(data,status) {
 document.getElementById('stats').innerHTML =
  '<span>Ball:' + data.ballPosition + '</span><br>' +
  '<span>Table:' + data.tableState + '</span><br>' +
  '<span>Demo Mode: ' + data.demoMode.state + '</span><br>' +
  '<span>Leds: ' + data.ledStatus.running + ' ' + data.ledStatus.pattern + '</span><br>' +
  '<span>Movie Status: ' + data.movieStatus + '</span><br>';
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
  This is for SandTable administrative tasks.<br>
  Please leave immediately unless you really know what you are doing.
 </div>
%end

<form method="post" action="admin">
 {{!form}}
 <button class="doit" name="action" type="submit" value="update">Update</button>
</form>

<form method="post" action="admin">
%for k,v in iter(sorted(actions.items())):
 %if v[1]:
  <button class="doit" name="action" type="submit" value="{{k}}">{{v[1]}}</button><br>
 %end
%end
</form>

