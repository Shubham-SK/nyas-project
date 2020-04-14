function select_change() {
  var z = document.getElementById("form_action").selectedIndex;
  var z1 = document.getElementsByTagName("option")[z].value;
}
function myfunction() {
  //if (validation()) {
  // Calling Validation function.
  //select option value from select tag and storing it in a variable.
  var x = document.getElementById("form_action").selectedIndex;
  var action = document.getElementsByTagName("option")[x].value;
  if (action !== "") {
    document.getElementById("form_id").action = action;
    document.getElementById("form_id").submit();
  } else {
    alert("Please set form action");
  }
  //}
}
