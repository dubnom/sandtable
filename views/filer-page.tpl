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
  $('<input />').attr('type','hidden').attr('name',name).attr('value',value).appendTo('#files');
  $('<input />').attr('type','hidden').attr('name',name2).attr('value',value2).appendTo('#files');
  document.getElementById('files').action = action;
  document.getElementById('files').submit();
}
</script>

<form method="post" action="filer">
 <div class="filerbox">
  <select class="filer" name="filetype" onchange="this.form.submit()">
   {{!options}}
  </select>
 </div>
</form>

<form id="files" method="post" action="filer">
 <input type="hidden" name="filetype" value="{{ft}}">
 <span class="filerTitle">{{path}}</span>
 <table id="filetable">
  {{!table}}
 </table>
</form>
