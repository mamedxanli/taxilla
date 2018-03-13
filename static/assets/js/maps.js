function initMap() {
  var mapDiv = document.getElementById('map');
  var defaultLatLng = {lat: 40.375, lng: 49.852};
  var map = new google.maps.Map(mapDiv, {
    center: defaultLatLng,
    zoom: 15
  });
  var pickupInput = document.getElementById('id_pickup');
  var dropoffInput = document.getElementById('id_dropoff');
  var pickupDataInput = document.getElementById('id_pickup_data');
  var dropoffDataInput = document.getElementById('id_dropoff_data');
  var geolocationEnabled = document.getElementById('id_geolocation');
  var markers = [];
  
  //MOVE MAP INSTEAD OF MARKER maybe?
  // Intialise a pickup marker
  // Add events like: http://www.w3schools.com/tags/ref_eventattributes.asp
  var pickupMarker = new google.maps.Marker({
    position: getPickupMarkerPosition(),
    map: map,
    draggable: true,
  });
  
  // Whenever user changes the marker - update the map bounds
  pickupMarker.addListener('dragend', updateMap);
  // and the address bar info
  pickupMarker.addListener('dragend', function(e) {
    latlng = pickupMarker.getPosition();
    pickupReverseGeocode(latlng);
  });
  markers.push(pickupMarker)
  updateMap();
  // Initialise a dropoff marker
  function createDropOffMarker () {
    var image = 'https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png';
    dropoffMarker = new google.maps.Marker({
      position: getDropoffMarkerPosition(),
      map: map,
      draggable: true,
      icon: image,
    });
    dropoffMarker.addListener('dragend', updateMap);
    dropoffMarker.addListener('dragend', function(e) {
      latlng = dropoffMarker.getPosition();
      dropoffReverseGeocode(latlng);
    });
    markers.push(dropoffMarker);
    updateMap();
  }
  
  // Create dropoff marker straight away if the data is there
  if (dropoffInput.value && dropoffDataInput.value ) {
    if (typeof dropoffMarker === 'undefined' || dropoffMarker === null) {
      createDropOffMarker();
    }
  }
  
  // Initialise pickup autocomplete
  var options = {
    types: ['address'],
    componentRestrictions: {country: 'az'}
  };
  pickupAutocomplete = new google.maps.places.Autocomplete(pickupInput, options);
  // Whenever user pick a result from autocomplete - update the map
  pickupAutocomplete.addListener('place_changed', pickupAutocompleteUpdateMap);
  
  // Initialise dropoff autocomplete
  var options = {
    types: ['address'],
    componentRestrictions: {country: 'az'}
  };
  dropoffAutocomplete = new google.maps.places.Autocomplete(dropoffInput, options);
  // Whenever user pick a result from autocomplete - update the map
  dropoffAutocomplete.addListener('place_changed', dropoffAutocompleteUpdateMap);
  
  // Put the markers if there's already an address
  function getPickupMarkerPosition() {
    if (pickupInput.value && pickupDataInput.value !== "{}" && pickupInput.value !== null) {
      var latlng = JSON.parse(pickupDataInput.value).geometry.location;
      return latlng;
    } else {
      return defaultLatLng;
    }
  }
  
  function getDropoffMarkerPosition() {
    if (dropoffInput.value && dropoffDataInput.value !== "{}" && dropoffInput.value !== null) {
      var latlng = JSON.parse(dropoffDataInput.value).geometry.location;
      return latlng;
    } else {
      return defaultLatLng;
    }
  }
  
  // Initialise geocoder
  var geocoder = new google.maps.Geocoder;

  // Try HTML5 geolocation.
  if (geolocationEnabled.value !== 'False' && navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      var latlng = new google.maps.LatLng(pos);
      //updateMap();
      if (pickupInput && !pickupInput.value) {
        pickupReverseGeocode(pos);
        pickupMarker.setPosition(latlng);
      };
    });
  }

  // Update the map and the fields when autocomplete completes
  function pickupAutocompleteUpdateMap() {
    var place = pickupAutocomplete.getPlace();
    document.getElementById("id_pickup_data").value = JSON.stringify(place);
    pickupMarker.setPosition(place.geometry.location);
    updateMap();
  }
  
  function dropoffAutocompleteUpdateMap() {
    var place = dropoffAutocomplete.getPlace();
    document.getElementById("id_dropoff_data").value = JSON.stringify(place);
    if (typeof dropoffMarker === 'undefined' || dropoffMarker === null) {
      createDropOffMarker();
    }
    dropoffMarker.setPosition(place.geometry.location);
    updateMap();
  }
  
  // Reverse geocode the pickup latlng to a place
  function pickupReverseGeocode(pos) {
    geocoder.geocode({'location': pos}, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        if (results[0]) {
          pickupInput.value = results[0].formatted_address;
          document.getElementById("id_pickup_data").value = JSON.stringify(results[0]);
          updateMap();
        }
      } else {
        window.alert('Geocoder failed due to: ' + status);
      }
    });
  }
  
  // Reverse geocode the dropoff latlng to a place
  function dropoffReverseGeocode(pos) {
    geocoder.geocode({'location': pos}, function(results, status) {
      if (status === google.maps.GeocoderStatus.OK) {
        if (results[0]) {
          dropoffInput.value = results[0].formatted_address;
          document.getElementById("id_dropoff_data").value = JSON.stringify(results[0]);
          updateMap();
        }
      } else {
        window.alert('Geocoder failed due to: ' + status);
      }
    });
  }
  
  // Function to update the map by LatLng object
  function updateMap() {
    var bounds = new google.maps.LatLngBounds();
    for (var i = 0; i < markers.length; i++) {
      bounds.extend(markers[i].getPosition());
    }
    map.fitBounds(bounds);
  }

}