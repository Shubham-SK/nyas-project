var x = document.getElementById("demo");

var today = new Date();
todayStr = today.getFullYear() + '-' + ('0' + (today.getMonth()+1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);

var dailyLimit = new Date();
dailyLimit.setDate(today.getDate()+15);
var dailyStr = dailyLimit.getFullYear() + '-' + ('0' + (dailyLimit.getMonth()+1)).slice(-2) + '-' + ('0' + dailyLimit.getDate()).slice(-2);

document.getElementById("start").setAttribute("min", todayStr);
document.getElementById("end").setAttribute("max", dailyStr);

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(showPosition);
} else {
  x.innerHTML = "Geolocation is not supported by this browser.";
}

function showPosition(position) {
  document.getElementById("lat").value = position.coords.latitude;
  document.getElementById("lon").value = position.coords.longitude;
  // x.innerHTML = "latitude: "+position.coords.latitude+"longitude: "+position.coords.longitude;
}
