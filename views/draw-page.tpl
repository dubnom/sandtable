<table class="main">
 <tr>
  <td valign="TOP">
   %for num, sandy in enumerate(sandables):
    %style = 'selected' if sandy == sandable else 'sandable'
    <a href="draw?method={{sandy}}"><img src="images/{{sandy}}.png" width="75" height="60" class="{{style}}" alt="{{sandy}}"></a>
    %if 2 == num % 3:
     <br>
    %end
   %end
  </td>
  <td valign="TOP">
   <center>
    <img class="plan" src="{{imagefile}}" width="{{width}}" height="{{height}}"><br>
    %if errors:
      <div class="error">Error: {{errors}}</div>
    %end
    {{!editor}}
   </center>
  </td>
 </tr>
</table>
