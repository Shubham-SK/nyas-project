var location_recorded = false;
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

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

function showPosition(position) {
  document.getElementById("lat").value = position.coords.latitude;
  document.getElementById("lon").value = position.coords.longitude;
  // alert("Location data recorded.");
    location_recorded = true;
}

function checkLocation() {
    if (location_recorded) {
        document.querySelector("#wait_msg").innerHTML = "Submitting...";
        document.querySelector("#loader").hidden = false;
        document.querySelector("#login_form").submit();
    } else {
        console.log("location not found");
    }
}

function waitForLocation() {
    document.querySelector("#wait_msg").innerHTML = "Waiting for location data...";
    document.querySelector("#loader").hidden = false;
    checkLocation();
    window.setInterval(checkLocation, 300);
}

function showHide(table, card) {
  if (table == null) return;

  table.hidden=false;
  card.hidden=true;
  return table;
}

function toggleActive(on, off) {
  on.className += " active";
  off.className = off.className.replace(" active", "");
}

function toggle(toggleVal) {
  var tableView = document.getElementById("tabular-view-scheduling");
  var cardView = document.getElementById("card-view-scheduling");
  var tableViewShopping = document.getElementById("tabular-view-shopping");
  var cardViewShopping = document.getElementById("card-view-shopping");
  var listToggle = document.getElementById("list-btn");
  var galleryToggle = document.getElementById("gallery-btn");

  if (toggleVal == 'list') {
    shown = showHide(tableView, cardView);
    shownShop = showHide(tableViewShopping, cardViewShopping);
  } else {
    shown = showHide(cardView, tableView);
    shownShop = showHide(cardViewShopping, tableViewShopping);
  }

  if ((shown && shown.id.includes("tabular")) || (shownShop && shownShop.id.includes("tabular")))
    toggleActive(listToggle, galleryToggle);
  else
    toggleActive(galleryToggle, listToggle);
}

// function adjustSearchHeight() {
//   // document.querySelector("tabular-view").style.height = `${document.querySelector("pills-update").clientHeight}px`;
//   alert(document.getElementById("find-stores-form").offsetHeight);
//   // setTimeout(() => { var height = (parseInt(document.getElementById("shopping-form").offsetHeight)+100).toString(); document.getElementById("tabular-view").style.height = height+"px";}, 200);
// }
