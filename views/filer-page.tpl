<script>
function myDelete(nm,fn,ft) {
  var deleted = confirm( "Permanently delete " + nm + "?" );
  if (deleted == true) {
    $.post("filer/delete", { nm: nm, filename: fn, ft: ft }, function(data,status) {
      if (data.result) {
        document.getElementById(fn).innerHTML = '<span class="filername">' + data.text + '</span>'; }
      else {
        alert( data.text ); }
    });
  }
}
function myRename(nm,fn,ft) {
  var newName = prompt( "Rename " + nm, nm);
  if (newName != null) {
    $.post("filer/rename", {nm: nm,  oldname: fn, newname: newName, ft: ft }, function(data,status) {
      if (data.result) {
        document.getElementById(fn).innerHTML = '<span class="filername">' + data.text + '</span>'; }
      else {
        alert( data.text ); }
    });
  }
}
function mySubmit(action,name,value,name2,value2) {
  if (action === 'draw' && name === 'action' && value.toLowerCase() === 'load' && name2 === '_loadname') {
    window.location.href = '/?view=draw&loadname=' + encodeURIComponent(value2);
    return;
  }
  $('<input />').attr('type','hidden').attr('name',name).attr('value',value).appendTo('#files');
  $('<input />').attr('type','hidden').attr('name',name2).attr('value',value2).appendTo('#files');
  document.getElementById('files').action = action;
  document.getElementById('files').submit();
}
</script>

<form method="post" action="/filer" class="auto_submit_form">
 <div class="filerbox">
  <select class="filer" name="filetype">
   {{ options|safe }}
  </select>
 </div>
</form>

{% if upload %}
 <form enctype="multipart/form-data" method="post">
  <div class="savebox">
   <input type="hidden" name="filetype" value="{{ft}}"/>
   <input type="hidden" name="directory" value="{{path}}"/>
   <input class="upload" name="_file" type="file" accept="{{ftfilter}}" required/>
   <button class="upload" name="action" type="submit" value="upload">Upload</Button>
  </div>
 </form>
{% endif %}

<form id="files" method="post" action="filer">
 <input type="hidden" name="filetype" value="{{ft}}"/>
 <span class="filerTitle">{{path}}</span>
 {% if ft == 'Saved Drawings' %}
  <div class="filerbox" style="margin-top: 6px; margin-bottom: 8px;">
   <button class="load" type="submit" name="directory" value="{{saved_directory}}">Saved only</button>
   <button class="load" type="submit" name="directory" value="{{store_root}}">Top level</button>
  </div>
 {% endif %}
 <table id="filetable">
  {{ table|safe }}
 </table>
</form>
