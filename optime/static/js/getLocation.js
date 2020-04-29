function setDates() {
  var today = new Date();
  todayStr = today.getFullYear() + '-' + ('0' + (today.getMonth()+1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);

  var dailyLimit = new Date();
  dailyLimit.setDate(today.getDate()+15);
  var dailyStr = dailyLimit.getFullYear() + '-' + ('0' + (dailyLimit.getMonth()+1)).slice(-2) + '-' + ('0' + dailyLimit.getDate()).slice(-2);

  document.getElementById("start").setAttribute("min", todayStr);
  document.getElementById("start").setAttribute("max", dailyStr);
  document.getElementById("end").setAttribute("min", todayStr);
  document.getElementById("end").setAttribute("max", dailyStr);
}

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(showPosition);
} else {
  alert("Geolocation is not supported by this browser.");
}

function showPosition(position) {

  document.getElementById("lat").value = position.coords.latitude;
  document.getElementById("lon").value = position.coords.longitude;
  alert("Location data recorded.");
}
