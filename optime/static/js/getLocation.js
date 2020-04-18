var x = document.getElementById("demo");

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
