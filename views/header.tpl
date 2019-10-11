<html>
<head>
%if jQuery:
 <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
 <script>
  $(function() {
   $(".auto_submit_form").change(function() {
    this.submit();
   });
  });
 </script>
%end
%if jQueryUI:
 <link rel="stylesheet" href="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.3/themes/smoothness/jquery-ui.css" />
 <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.3/jquery-ui.min.js"></script>
%end
 <script>
  function randomInt( field, min, max ) {
   number = min + Math.floor( Math.random()*(max - min));
   field.value = number; }
  function randomFloat( field, min, max ) {
   number = min + Math.random() * (max - min);
   number = 0.0001 * Math.floor( number * 10000 );
   field.value = number; }
 </script>
<meta name="viewport" content="width=device-width, user-scalable=yes" />
{{!meta}}
<link rel="stylesheet" type="text/CSS" href="sandtable.css" />
<title>Sand Table - {{title}}</title>
</head>
