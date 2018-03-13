var id, options, loc;

function httpGetAsync(url)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", url, true); // true for asynchronous
    xmlHttp.send();
}

function encodeQueryData(data)
{
   var ret = [];
   for (var d in data)
      ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
   return ret.join("&");
}

function success(pos) {
  // We don't want to update location if its the same
  if (JSON.stringify(pos.coords) === JSON.stringify(loc)) {
    return;
  }
  loc = pos.coords;
  latLng = {'lat': loc.latitude, 'lng': loc.longitude};
  data = encodeQueryData(latLng);
  if (window.location.port === '80') {
    port = '';
  } else {
    port = ':' + window.location.port;
  }
  url = window.location.protocol + '//' + window.location.hostname + port + '/vehicles/vehicle_location_update/' + vehicle_id + '/' + travel_id + '/?' + data;
  httpGetAsync(url);
  if (typeof gmap !== 'undefined') {
    if (typeof driverMarker === 'undefined') {
      var driverMarker = new google.maps.Marker({
        position: latLng,
        map: gmap,
      });
    } else {
      var latlng = new google.maps.LatLng(latLng);
      pickupMarker.setPosition(latlng);
    }
  }
}

function error(err) {
  console.warn('ERROR(' + err.code + '): ' + err.message);
}

options = {
  enableHighAccuracy: false,
  timeout: 15000,
  maximumAge: 0
};

id = navigator.geolocation.watchPosition(success, error, options);
