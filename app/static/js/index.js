var start = new Date();
start.setHours(0,0,0,0);

var end = new Date();
end.setHours(23,59,59,999);
var list_of_candidates = '';
var map;

$(function () {
    $('#datepicker').datepicker({
        autoclose: true,
        onSelect: function(dateText, inst) {
            start = $(this).datepicker( 'getDate' );
            start.setHours(0,0,0,0);
            end = $(this).datepicker( 'getDate' );
            end.setHours(23,59,59,999);
            ajaxFetch();
        }
    });
});

var markers = [];
$(document).ready(function(){
    ajaxFetch();

    $('.btn').click(function() {
        if ( $(this).hasClass("disabled") ) {return;}
        if ( $(this).hasClass("btn-success") ) {
            $(this).removeClass("btn-success")
	        $(this).addClass("btn-danger")
	        $(this).removeClass("active")
	    } else {
	        // assume we have btn-danger
	        $(this).removeClass("btn-danger")
	        $(this).addClass("btn-success")
	        $(this).addClass("active")
	    }
        for (var i = 0; i < markers.length; i++) {
          markers[i].setMap(null);
        }
        markers = [];
	    // we have updated the button states now we need to use them to fetch the new map
        list_of_candidates = '';
	    $('.btn').each(function() {
	        if ( $(this).hasClass("btn-success") ) {
	            list_of_candidates = list_of_candidates + $(this).attr('id') + ',';
            }
	    });
	    list_of_candidates = list_of_candidates.substring(0, list_of_candidates.length - 1);
        ajaxFetch();
    });
});

function ajaxFetch() {
        $.ajax({ url: "/fetch",
        type: 'GET',
        data: {dateTime_start: start, dateTime_end: end, candidates: list_of_candidates},
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        context: document.body,
        success: function(data){
            candidateKeys = Object.keys(data.stats)
            for(var i = 0; i < candidateKeys.length; i++) {
                if(candidateKeys[i] === '') {
                    continue;
                }
                $('#' + candidateKeys[i] + '-avg').text(data.stats[candidateKeys[i]]['avg_sentiment'].toFixed(4))
                $('#' + candidateKeys[i] + '-num').text(data.stats[candidateKeys[i]]['length'])
            }

            for(var i = 0; i < data.tweets.length; i++) {
                if(data.tweets[i].sentiment < 0) {
                    var marker = new google.maps.Marker({
                        position: {lat:parseFloat(data.tweets[i].latitude), lng:parseFloat(data.tweets[i].longitude)},
                        icon: './static/images/red.png',
                        title: data.tweets[i].text + '\nSentiment: ' + data.tweets[i].sentiment,
                        map: map,
                    });
                    markers.push(marker);
                } else if (data.tweets[i].sentiment == 0) {
                    var marker = new google.maps.Marker({
                        position: {lat:parseFloat(data.tweets[i].latitude), lng:parseFloat(data.tweets[i].longitude)},
                        icon: './static/images/neutral.png',
                        title: data.tweets[i].text + '\nSentiment: ' + data.tweets[i].sentiment,
                        map: map
                    });
                    markers.push(marker);
                } else {
                    var marker = new google.maps.Marker({
                        position: {lat:parseFloat(data.tweets[i].latitude), lng:parseFloat(data.tweets[i].longitude)},
                        icon: './static/images/green.png',
                        title: data.tweets[i].text + '\nSentiment: ' + data.tweets[i].sentiment,
                        map: map
                    });
                    markers.push(marker);
                }
            }
        }});
}

function initMap() {
// 40.489814, -96.887740
  var myLatLng = {lat: 40.489814, lng: -96.887740};

  map = new google.maps.Map(document.getElementById('map'), {
    zoom: 4,
    center: myLatLng
  });
}
