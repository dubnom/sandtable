<form enctype="multipart/form-data" method="post">
 <div class="savebox">
  <input class="upload" name="_file" type="file" required/>
  <button class="upload" name="action" type="submit" value="upload">Upload</Button>
 </div>
</form>

<form method="post" action="draw">
 <input name="method" type="hidden" value="Picture">
 <table>
  %for i, (f, filename) in enumerate(pictures):
    %if not i % columns:
      <tr>
    %end
    <td class="picture" valign="bottom">
     <button class="picture" type="submit" name="filename" value="{{filename}}">
      <img src="{{filename}}" width="160" align="center">
      <p class="picturename">{{f}}</p>
     </button>
    </td>
    %if not (i+1)%columns:
      </tr>
    %end
  %end
  %if i % columns:
    </tr>
  %end
 </table>
</form>
