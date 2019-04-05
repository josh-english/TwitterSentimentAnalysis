var start = new Date();
start.setHours(0,0,0,0);

var end = new Date();
end.setHours(23,59,59,999);
var list_of_candidates = 'trump';
var map;

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