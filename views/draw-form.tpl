<style>
  .d_input, .d_text { display: block }
  .d_text { margin-bottom:120px; width:95%; padding: .4em; }
  .d_fieldset { padding:0; border:0; margin-top:25px; };
</style>
<script>
  // Helper function to download a file
  function download_file(fileURL, fileName) {
    // for non-IE
    if (!window.ActiveXObject) {
      var save = document.createElement('a');
      save.href = fileURL;
      save.target = '_blank';
      var filename = fileURL.substring(fileURL.lastIndexOf('/')+1);
      save.download = fileName || filename;
      if ( navigator.userAgent.toLowerCase().match(/(ipad|iphone|safari)/) && navigator.userAgent.search("Chrome") < 0) {
        document.location = save.href; 
      } else {
        var evt = new MouseEvent('click', {'view': window, 'bubbles': true, 'cancelable': false });
	save.dispatchEvent(evt);
	(window.URL || window.webkitURL).revokeObjectURL(save.href);
      }	
    }

    // for IE < 11
    else if ( !! window.ActiveXObject && document.execCommand) {
       var _window = window.open(fileURL, '_blank');
       _window.document.close();
       _window.document.execCommand('SaveAs', true, fileName || fileURL)
       _window.close();
    }
  }
</script>
<script>
  $( function() {
    var dialog, form,
      name = $("#name"),
      format = $("#format"),
      allFields = $([]).add(format).add(name),
      tips = $(".validateTips");

    function updateTips(t) {
      tips
        .text(t)
        .addClass("ui-state-highlight");
      setTimeout(function() {
        tips.removeClass( "ui-state-highlight", 1500 );
      }, 500 );
    }
 
    function checkLength( o, n, min, max ) {
      if ( o.val().length > max || o.val().length < min ) {
        o.addClass( "ui-state-error" );
        updateTips( "Length of " + n + " must be between " +
          min + " and " + max + "." );
        return false;
      } else {
        return true;
      }
    }
 
    function checkRegexp( o, regexp, n ) {
      if ( !( regexp.test( o.val() ) ) ) {
        o.addClass( "ui-state-error" );
        updateTips( n );
        return false;
      } else {
        return true;
      }
    }

    function exportDrawing() {
      var valid = true;
      allFields.removeClass( "ui-state-error" );

      valid = valid && checkLength(name, "name", 1, 80);
      valid = valid && checkRegexp(name, /^[0-9a-zA-Z]+$/i, "Only letters and numbers");
      if(valid) {
        var my_name = name.val(),
            my_format = format.val(),
            my_filename = my_name + "." + my_format,
            my_formdata = $('#mainform').serializeArray().reduce(function(obj, item) {
              obj[item.name] = item.value;
              return obj;
              }, {});
        my_formdata._name = my_name;
        my_formdata._format = my_format;
        my_formdata.action = "export";
        $.post( "", my_formdata, function(data) {
          download_file( "/data/" + my_filename, my_filename );
        }); 
        dialog.dialog("close");
      }
      return valid;
    }

    dialog = $("#dialog-export").dialog({
      autoOpen: false,
      height: 400,
      width: 350,
      modal: true,
      buttons: {
        "Export": exportDrawing,
        Cancel: function() {
          dialog.dialog("close");
        }
      },
      close: function() {
        form[0].reset();
        allFields.removeClass( "ui-state-error" );
      }
    });

    form = dialog.find("form").on("submit", function(event) {
      event.preventDefault();
      exportDrawing();
    });

    $("#nexport").button().on("click", function() {
      dialog.dialog("open");
    });

  });
</script>
<script>
  // Save to Playlist
  $( function() {
    var dialog, form,
      pname = $("#pname"),
      playlist = $("#playlist"),
      allFields = $([]).add(playlist).add(pname),
      tips = $(".validateTips");

    function updateTips(t) {
      tips
        .text(t)
        .addClass("ui-state-highlight");
      setTimeout(function() {
        tips.removeClass( "ui-state-highlight", 1500 );
      }, 500 );
    }
 
    function checkLength( o, n, min, max ) {
      if ( o.val().length > max || o.val().length < min ) {
        o.addClass( "ui-state-error" );
        updateTips( "Length of " + n + " must be between " +
          min + " and " + max + "." );
        return false;
      } else {
        return true;
      }
    }
 
    function checkRegexp( o, regexp, n ) {
      if ( !( regexp.test( o.val() ) ) ) {
        o.addClass( "ui-state-error" );
        updateTips( n );
        return false;
      } else {
        return true;
      }
    }

    function addToPlaylist() {
      var valid = true;
      allFields.removeClass( "ui-state-error" );

      valid = valid && checkLength(pname, "pname", 1, 80);
      valid = valid && checkLength(playlist, "playlist", 1, 80);
      valid = valid && checkRegexp(pname, /^[0-9a-zA-Z]+$/i, "Only letters and numbers");
      valid = valid && checkRegexp(playlist, /^[0-9a-zA-Z]+$/i, "Only letters and numbers");
      if(valid) {
        var my_pname = pname.val(),
            my_playlist = playlist.val(),
            my_formdata = $('#mainform').serializeArray().reduce(function(obj, item) {
              obj[item.name] = item.value;
              return obj;
              }, {});
        my_formdata._name = my_pname;
        my_formdata._playlist = my_playlist;
        my_formdata.action = "add";
        $.post( "", my_formdata );
        dialog.dialog("close");
      }
      return valid;
    }

    dialog = $("#dialog-add").dialog({
      autoOpen: false,
      height: 400,
      width: 350,
      modal: true,
      buttons: {
        "Save": addToPlaylist,
        Cancel: function() {
          dialog.dialog("close");
        }
      },
      close: function() {
        form[0].reset();
        allFields.removeClass( "ui-state-error" );
      }
    });

    form = dialog.find("form").on("submit", function(event) {
      event.preventDefault();
      exportDrawing();
    });

    $("#nadd").button().on("click", function() {
      dialog.dialog("open");
    });
  });
</script>

<div id="dialog-export" title="Export Drawing">
  <p class="validateTips">All form fields are required.</p>
  <form>
    <fieldset class="d_fieldset">
      <label for="format">Format</label>
      <select name="format" id="format" class="d_input ui-widget-content ui-corner-all">
        <option value="svg">SVG</option>
        <option value="thr">THR</option>
        <option value="gcode">GCODE</option>
        <option value="xy">XY</option>
      </select>
      <label for="name">Name</label>
      <input type="text" name="name" id="name" value="" class="d_text ui-widget-content ui-corner-all">
      <input type="submit" tabindex="-1" style="position:absolute; top:-1000px">
    </fieldset>
  </form>
</div>

<div id="dialog-add" title="Add to Playlist">
  <p class="validateTips">All form fields are required.</p>
  <form>
    <fieldset class="d_fieldset">
      <label for="playlist">Playlist</label>
      <select name="playlist" id="playlist" class="d_input ui-widget-content ui-corner-all">
        {{!playlists}}
      </select>
      <label for="pname">Name</label>
      <input type="text" name="pname" id="pname" value="" class="d_text ui-widget-content ui-corner-all"> 
    </fieldset>
  </form>
</div>

<span class="drawtime">{{!drawinfo}}{{!help}}</span>
<form method="post" action="draw" id="mainform">
 <input name="method" type="hidden" value="{{sandable}}">
 {{!dialog}}
 <button class="redraw" name="action" type="submit" value="refresh">Redraw Screen</button>
 <button class="random" name="action" type="submit" value="random">Random!</button>
 <button class="doit" name="action" type="submit" value="doit">Draw in Sand!</button>
 <button class="abort" name="action" type="submit" value="abort">Abort!</button>
</form>
<div class="savebox">
 <button class="" id="nadd">Add to Playlist</button>
 <button class="" id="nexport">Export</button>
</div>

<script>
 $("#nadd").removeClass("ui-button");
</script>
