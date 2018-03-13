// this script sends ajax request to receive the available drivers

var pickup = "#id_pickup",
    dropoff = "#id_dropoff",
    psn_no = "#id_no_of_passengers",
    date = "#id_date_time_0",
    time = "#id_date_time_1",
    form_id = '#travel_form',
    locations = pickup + ',' + dropoff,
    carSelect = $('#id_assigned_vehicle'),
    duration,
    distance,
    error_msg = 'Please correct the error below',
    errors_msg = 'Please correct the errors below',
    loadingDiv = "<div id='loadingDiv'>Please wait...</div>",
    errorDiv = "<div id='errorDiv'></div>",
    directions_shown = $.Deferred(),
    booking_times = ['now'];


// below showDirections is copied from maps_view_for_driver.js with some modifications
function showDirections(){
    console.log('showDirections run');
    var directionsService = new google.maps.DirectionsService(),
        directionsDisplay = new google.maps.DirectionsRenderer(),
        origin = document.getElementById(pickup.substring(1)).value,
        destination = document.getElementById(dropoff.substring(1)).value;

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
            //Gets all the readonly fields
            var myList = document.getElementsByClassName("grp-readonly");
            //Fills Duration
            duration = directionsDisplay.directions.routes[0].legs[0].duration.text;
            myList[0].innerHTML = duration;
            //Fills Distance
            distance = directionsDisplay.directions.routes[0].legs[0].distance.text
            myList[1].innerHTML = distance;
            directions_shown.resolve();
        }
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

var csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function main() {
    var url = window.location.pathname;
    createBookingTimes();
    grp.jQuery('.hasDatepicker').datepicker('option', 'firstDay', 1);
    grp.jQuery('.hasTimepicker').grp_timepicker({time_list: booking_times});
    changeTimepickerStyle();

    if (url.indexOf("travel/add") != -1) {
        console.log("main_add");
        errorsAfterPost();
        watchLocations();
        watchPassengerNumber();
        deleteOptions();
    } else {
        console.log("main_edit");
        let loop = setInterval(function(){
            if (typeof google === 'object') {
                showDirections();
                $.when(directions_shown).then(function() {runAjax();});
                clearInterval(loop);
            }
        }, 500);
        watchLocations();
        watchPassengerNumber();
        watchDateTime();
    }
}

function errorsAfterPost() {
    var loop = setInterval(function() {
        let pickup_field = "#id_pickup",
            dropoff_field = "#id_dropoff",
            err_p_elem_text = $(form_id + ' p.errornote').text();
        if ((err_p_elem_text.indexOf(error_msg) > -1) || (err_p_elem_text.indexOf(errors_msg) > -1)) {
            if(($(pickup_field).val() != "")&&($(dropoff_field).val() != "")) {
                clearInterval(loop);
                setTimeout(showDirections, 1000);
                $.when(directions_shown).then(function() {
                    if (($(date).val() != "")&&($(time).val() != "")) {
                        runAjax();
                    } else {
                        watchDateTime();
                    }
                });
            }
        }
    }, 500);
}

function watchLocations () {
    $(locations).on('change', function (){
        $(this).blur(function (){
            if(($(pickup).val() != "")&&($(dropoff).val() != "")) {
                showDirections();
                if (($(date).val() != "")&&($(time).val() != "")) {
                    runAjax();
                } else {
                    watchDateTime();
                }
            }
        })
    })
}

function watchDateTime () {
    var date_value = $(date).val(),
        time_value = $(time).val();

    var loop = setInterval(function () {
        if(($(date).val() != "")&&($(time).val() != "")&&(($(date).val() != date_value)||($(time).val() != time_value))) {
            if(($(pickup).val() != "")&&($(dropoff).val() != "")) {
                date_value = $(date).val();
                time_value = $(time).val();
                runAjax();
            }
        } 
    }, 1000);
}

function runAjax () {
    $("#duration_id").val(duration);
    $("#distance_id").val(distance);

    var data = $(form_id).serialize(),
        errorDiv_id = '#errorDiv',
        loadingDiv_id = '#loadingDiv';

    deleteOptions();
    $('*' + loadingDiv_id).each(function() {$(this).remove()})
    $('*' + errorDiv_id).each(function() {$(this).remove()})
    carSelect.after(loadingDiv);
    carSelect.hide();

    $.ajax({
        url: '',
        data: data,
        dataType: 'json',
        type: "POST",
        success: function (responseJson) {
            $('*' + loadingDiv_id).each(function() {$(this).remove()});
            carSelect.show();
            if ($.isEmptyObject(responseJson)) {
                carSelect.hide();
                $('*' + errorDiv_id).each(function() {$(this).remove()})
                message = "We could not find any drivers for this route";
                carSelect.after(errorDiv);
                $(errorDiv_id).html(message);
            }
            createOptions(responseJson);
        },
        error: function(jqXHR, textStatus, errorThrown) {
            $('*' + loadingDiv_id).each(function() {$(this).remove()})
            carSelect.show();
            carSelect.after(errorDiv);
            error_message = jqXHR.status + ' ' + textStatus + ": " + errorThrown;
            msg = ". Please contact administrator to resolve the problem";
            $(errorDiv_id).html(error_message + msg);
        }
    })
}

function deleteOptions () {
    $('#id_assigned_vehicle option').each(function () {
        if (!( $(this).html() == '---------' )) {
            $(this).remove();
        }
    });
}

function createOptions (obj) {
    deleteOptions();
    $.each(obj, function (key, value) {
        carSelect.append($('<option/>', { 
            value: key,
            text : value 
        }));
    })

}

function createBookingTimes() {
    for (let h = 0; h < 24; h++) {
        for (let m = 0; m < 60; ) {
            if ((h.toString()).length == 1) {
                if ((m.toString()).length == 1) {
                    booking_times.push('0' + h + ':' + m + '0');
                } else {
                    booking_times.push('0' + h + ':' + m);
                }
            } else {
                if ((m.toString()).length == 1) {
                    booking_times.push(h + ':' + m + '0');
                } else {
                    booking_times.push(h + ':' + m);
                }
            }
            m += 15;
        }
    }
}

function changeTimepickerStyle() {
    $('p.datetime > button.ui-timepicker-trigger').click(function () {
        $('#ui-timepicker').css({
            "position": "absolute",
            "left": "315px",
            "top": "350px", 
            "display": "block"
        });
    });
}

function watchPassengerNumber() {
    $('#id_no_of_passengers').on('change', function (){
        if(($(date).val() != "")&&($(time).val() != "")) {
            if(($(pickup).val() != "")&&($(dropoff).val() != "")) {
                runAjax();
            }
        }
    })
}