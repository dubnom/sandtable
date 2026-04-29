<span class="drawtime">{{ drawinfo|safe }}{{ help|safe }}</span>
<form method="post" action="/draw">
 <input name="method" type="hidden" value="{{sandable}}">
 <input id="drawNameInput" name="_name" type="hidden" value="{{ drawname or '' }}">
 {{ dialog|safe }}
 <button class="redraw" name="action" type="submit" value="refresh">Refresh</button>
 <button class="random" name="action" type="submit" value="random">Random!</button>
 <button class="doit" name="action" type="submit" value="doit">Draw Now!</button>
 <button class="abort" name="action" type="submit" value="abort">Abort!</button>
 <div class="savebox">
    <button class="save" name="action" type="submit" value="save" onclick="var n=prompt('Save drawing as', document.getElementById('drawNameInput').value || '{{ sandable }}'); if(n===null||!n.trim()){return false;} document.getElementById('drawNameInput').value=n.trim();">Save...</button>
    <button class="export" name="action" type="submit" value="export" onclick="var n=prompt('Export drawing as', document.getElementById('drawNameInput').value || '{{ sandable }}'); if(n===null||!n.trim()){return false;} document.getElementById('drawNameInput').value=n.trim();">Export...</button>
 </div>
</form>
