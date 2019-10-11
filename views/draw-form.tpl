<span class="drawtime">{{!drawinfo}}{{!help}}</span>
<form method="post" action="draw">
 <input name="method" type="hidden" value="{{sandable}}">
 {{!dialog}}
 <button class="redraw" name="action" type="submit" value="refresh">Redraw Screen</button>
 <button class="random" name="action" type="submit" value="random">Random!</button>
 <button class="doit" name="action" type="submit" value="doit">Draw in Sand!</button>
 <button class="abort" name="action" type="submit" value="abort">Abort!</button>
 <div class="savebox">
  <span class="save">Name</span>
  <input class="save" name="_name" type="string" size="40">
  <button class="save" name="action" type="submit" value="save">Save</button>
  <button class="export" name="action" type="submit" value="export">Export</button>
 </div>
</form>
