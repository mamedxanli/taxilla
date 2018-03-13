function initMap() {
  var mapDiv = document.getElementById('map');
  var defaultLatLng = {lat: 40.375, lng: 49.852};
  var map = new google.maps.Map(mapDiv, {
    center: defaultLatLng,
    zoom: 15,
    scrollwheel: false,
  });
  var pickup_js = eval ("(" + pickup_data + ")");
  var dropoff_js = eval ("(" + dropoff_data + ")");

  var pickupMarker = new google.maps.Marker({
    position: pickup_js.geometry.location,
    map: map,
  });

  var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png';
  var dropoffMarker = new google.maps.Marker({
    position: dropoff_js.geometry.location,
    map: map,
    icon: image,
  });

  var markers = [];
  markers.push(pickupMarker);
  markers.push(dropoffMarker);
  updateMap();

  function updateMap() {
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markers.length; i++) {
      bounds.extend(markers[i].getPosition());
    }
    map.fitBounds(bounds);
  }

}
