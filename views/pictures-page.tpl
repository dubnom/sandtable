<form enctype="multipart/form-data" method="post">
 <div class="savebox">
  <input class="upload" name="_file" type="file" required/>
  <button class="upload" name="action" type="submit" value="upload">Upload</Button>
 </div>
</form>

<form method="post" action="draw">
 <input name="method" type="hidden" value="Picture">
 <table>
  {% for f, filename in pictures %}
    {% if loop.index0 % columns == 0 %}
      <tr>
    {% endif %}
    <td class="picture" valign="bottom">
     <button class="picture" type="submit" name="filename" value="{{filename}}">
      <img src="{{filename}}" width="160" align="center">
      <p class="picturename">{{f}}</p>
     </button>
    </td>
    {% if loop.index % columns == 0 or loop.last %}
      </tr>
    {% endif %}
  {% endfor %}
 </table>
</form>
