function initMap() {
  var mapDiv = document.getElementById('map');
  var latitude = +document.getElementById('id_latitude').value;
  var longitude = +document.getElementById('id_longitude').value;
  // If no lat/lng is set - remove the map
  if (latitude === 0 && longitude === 0) {
    mapDiv.remove();
    return;
  }
  var latLng = {lat: latitude, lng: longitude};
  var map = new google.maps.Map(mapDiv, {
    center: latLng,
    zoom: 15,
    scrollwheel: false,
  });
  var vehicleMarker = new google.maps.Marker({
    position: latLng,
    map: map,
  });
}
