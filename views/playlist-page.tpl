<div class="historybox">
 <span class="historyTitle">Playlist</span><br><br>

 {% if status %}
    <div class="status">{{ status }}</div><br>
 {% endif %}
 {% if error %}
    <div class="error">Error: {{ error }}</div><br>
 {% endif %}

 {% if items and items|length %}
  <form method="post" action="playlist" style="margin-bottom: 12px;">
     <button class="doit" type="submit" name="action" value="drawall">Draw Playlist</button>
   <button class="delete" type="submit" name="action" value="clear" onclick="return confirm('Clear the entire playlist?');">Clear Playlist</button>
  </form>

  <table class="help" cellspacing="0" cellpadding="4" style="background-color: rgba(255,255,255,0.85);">
   <tr>
      <th class="help">Image</th>
    <th class="help">Title</th>
    <th class="help">Method</th>
    <th class="help">Added</th>
    <th class="help">Actions</th>
   </tr>
   {% for item in items %}
   <tr>
      <td class="help">
       {% if item.imageUrl %}
             <img src="{{ item.imageUrl }}" alt="{{ item.title }}" width="96" class="history" style="height: auto;">
       {% endif %}
      </td>
    <td class="help">{{ item.title }}</td>
        <td class="help"><a href="draw?method={{ item.method }}">{{ item.method }}</a></td>
        <td class="help">{{ item.createdText }}</td>
    <td class="help">
    <form method="post" action="playlist" style="display:inline;">
     <input type="hidden" name="action" value="moveup">
     <input type="hidden" name="id" value="{{ item.id }}">
     <button class="load" type="submit"{% if loop.first %} disabled{% endif %}>Up</button>
    </form>
    <form method="post" action="playlist" style="display:inline;">
     <input type="hidden" name="action" value="movedown">
     <input type="hidden" name="id" value="{{ item.id }}">
     <button class="load" type="submit"{% if loop.last %} disabled{% endif %}>Down</button>
    </form>
        <form method="post" action="playlist" style="display:inline;">
         <input type="hidden" name="action" value="draw">
         <input type="hidden" name="id" value="{{ item.id }}">
         <button class="doit" type="submit">Draw</button>
        </form>
     <form method="post" action="playlist" style="display:inline;">
      <input type="hidden" name="action" value="remove">
      <input type="hidden" name="id" value="{{ item.id }}">
      <button class="delete" type="submit">Remove</button>
     </form>
    </td>
   </tr>
   {% endfor %}
  </table>
 {% else %}
  <span class="navigation">Playlist is empty.</span>
 {% endif %}
</div>
