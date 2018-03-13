function getDirections(origin, destination){
    var directionsService = new google.maps.DirectionsService();
    var directionsDisplay = new google.maps.DirectionsRenderer();
    var travel = {
            origin : origin,
            destination : destination,
            travelMode : google.maps.DirectionsTravelMode.DRIVING
        },
        mapOptions = {
            mapTypeId: google.maps.MapTypeId.ROADMAP,
            scrollwheel: false,
        };

    gmap = new google.maps.Map(document.getElementById("map"), mapOptions);
    directionsDisplay.setMap(gmap);
    directionsService.route(travel, function(result, status) {
        if (status === google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(result);
        }
    });
}


function getLinks(org, dst){
    var data = navigator.userAgent;
    var device, prefix;
    var iOS = [/iPhone/gi, /iPad/gi, /iPod/gi];
    for (i = 0; i < iOS.length; i++) {
        if (data.search(iOS[i]) != -1) {
            device = 'iphone';
            break;
        }
    };
    if (data.search(/android/gi) != -1) {
            device = 'android';
    };
    var toPassenger = document.getElementById("toPassenger");
    var toDestination = document.getElementById("toDestination");
    var origin = org.geometry.location.lat + "," + org.geometry.location.lng;
    var destination = dst.geometry.location.lat + "," + dst.geometry.location.lng;
    if (device == 'iphone') {
        prefix = '<a href="comgooglemaps://?q=';
    } else if (device == 'android') {
        prefix = '<a href="google.navigation:q=';
    } else {
        toDestination.innerHTML = '<a href="https://maps.google.com?saddr=' + org.formatted_address + '&daddr=' + dst.formatted_address + '">See this map on Google Maps</a>';
    };
    if (device == 'iphone' || device == 'android') {
        toPassengerLink = prefix + origin + '">Route to passenger</a>';
        toPassenger.innerHTML = toPassengerLink;
        toDestinationLink = prefix + destination + '">Route to destination</a>';
        toDestination.innerHTML = toDestinationLink;
    } else {
        document.getElementById("hiddenTravelInfo").style.display = "none";
    };
};


function initMap() {
    // these two values are picked up from the template
    var pickup_js = eval ("(" + pickup_data + ")");
    var dropoff_js = eval ("(" + dropoff_data + ")");
    var origin = "" + pickup_js.formatted_address;
    var destination = "" + dropoff_js.formatted_address;

    getDirections(origin, destination);
    getLinks(pickup_js, dropoff_js);
}
