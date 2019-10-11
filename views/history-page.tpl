<form method="post" action="draw">
 <input name="action" type="hidden" value="load">
 <div class="historybox">
  <br><span class="historyTitle">Saved</span><br>
  %for n,t in zip(save,mtimes(save)):
   <button class="history" type="submit" name="_loadname" value="{{n}}"><img src="{{path}}{{n}}.png?{{t}}" alt="{{n}}"></button>
  %end
  <br><br><span class="historyTitle">History</span><br>
  %for n,t in zip(history,mtimes(history)):
   <button class="history" type="submit" name="_loadname" value="{{n}}"><img src="{{path}}{{n}}.png?{{t}}" alt="{{n}}"></button>
  %end
 </div>
</form>

