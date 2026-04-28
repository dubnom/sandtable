<form method="get" action="/draw">
 <div class="historybox">
  <br><span class="historyTitle">Saved</span><br>
    {% for item in save_items %}
   <button class="history" type="submit" name="loadname" value="{{item.name}}"><img src="{{item.path}}" alt="{{item.name}}"></button>
    {% endfor %}
  <br><br><span class="historyTitle">History</span><br>
    {% for item in history_items %}
   <button class="history" type="submit" name="loadname" value="{{item.name}}"><img src="{{item.path}}" alt="{{item.name}}"></button>
    {% endfor %}
 </div>
</form>

