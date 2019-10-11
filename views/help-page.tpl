<html>
<head>
 <link rel="stylesheet" type="text/CSS" href="sandtable.css" />
 <title>Sand Table - Help</title>
</head>
    
<body>
<pre class="text">
{{!overview}}
</pre>

<table class="help">
  %for sand in sandables:
    %sandable = sandableFactory( sand )
    <tr><th class="help" colspan="3">{{sand}}</th></tr>
    %for field in sandable.editor:
      <tr>
        <td class="help">{{field.name}}</td>
        <td class="help">{{field.prompt}}</td>
        <td class="help">{{field.units}}</td>
      </tr>
    %end
  %end
</table>

</body>
</html>

