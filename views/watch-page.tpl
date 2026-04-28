<script>
 function setVideo(el) {
  sel = el.options[el.selectedIndex].value;
  if(!sel)
   document.getElementById('vid').innerHTML = 'Choose Movie';
  else
   document.getElementById('vid').innerHTML = '<embed src="' + sel + '" name="Video" width="{{width}}" height="{{height}}" scale="tofit" autostart="true" pluginspage="http://www.apple.com/quicktime/download"></embed>';
 }
</script>

<form>
 <div class="loadbox">
  <select id="list" class="load" name="_loadname" onchange="setVideo(this)">
   <option>Pick a movie...</option>
  {% for fileName in fileNames %}
    <option value="{{path}}{{fileName}}">{{fileName.split('.')[0]}}</option>
  {% endfor %}
  </select>
 </div>
</form>
 
<div id="vid" style="width: {{width}}px; height: {{height}}px; border: 1px solid black;">Choose Movie</div>

{% if loadname %}
 <script>
  document.getElementById("list").selectedIndex={{ selected_index }};
  setVideo(document.getElementById("list"));
 </script>
{% endif %}

