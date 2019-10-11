<table class="main">
 <tr>
  <form method="post" action="lights">
   <td valign="TOP">
    %for num, pat in enumerate(ledPatterns):
      %style = 'ledselected' if pat == pattern else 'led'
      <button class="{{style}}" type="submit" name="method" value="{{pat}}">
       <img src="images/{{pat}}.png" width="100" height="80" alt="{{pat}}">
      </button>
      %if 2 == num % 3:
        <br>
      %end
    %end
   </td>
  </form>

  <td valign="TOP">
   <center>
   <h3>{{pattern}}</h3>
   <form method="post" action="lights" class="auto_submit_form">
    <input name="method" type="hidden" value="{{pattern}}">
    {{!editor}}
    <button class="doit" name="action" type="submit" value="doit">Lights!</button>
   </form>
   </center>
  </td>
 </tr>
</table>

