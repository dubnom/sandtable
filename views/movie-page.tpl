<form method="post">
 <div class="loadbox">
  <select class="load" name="_loadname">
   <option></option>
    {{!filenames}}
  </select>
  <button class="load" name="action" type="submit" value="load">Load</button>
  <span class="navigation"><a href="help" target="sand_help">Help!</a></span>
 </div>
 <textarea name="script" rows=34 cols="70">{{script}}</textarea>
 <div class="savebox">
  <input class="save" name="_name" type="string" size="30" value="{{name}}">
  <button class="save" name="action" type="submit" value="save">Save</button>
  <button class="preview" name="action" type="submit" value="preview">Preview</button>
  <button class="sand" name="action" type="submit" value="sand">Sand</button>
 </div>
</form>

