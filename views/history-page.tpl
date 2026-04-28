<form method="post" action="draw">
 <input name="action" type="hidden" value="load">
 <div class="historybox">
  <br><span class="historyTitle">Saved</span><br>
    {% for n,t in save_items %}
   <button class="history" type="submit" name="_loadname" value="{{n}}"><img src="{{path}}{{n}}.png?{{t}}" alt="{{n}}"></button>
    {% endfor %}
  <br><br><span class="historyTitle">History</span><br>
    {% for n,t in history_items %}
   <button class="history" type="submit" name="_loadname" value="{{n}}"><img src="{{path}}{{n}}.png?{{t}}" alt="{{n}}"></button>
    {% endfor %}
 </div>
</form>

