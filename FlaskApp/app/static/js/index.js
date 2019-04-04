$(document).ready(function(){
    var start = new Date();
    start.setHours(0,0,0,0);

    var end = new Date();
    end.setHours(23,59,59,999);
    var list_of_candidates = 'trump,orourke'

    $.ajax({ url: "/fetch",
            type: 'GET',
            data: {dateTime_start: start, dateTime_end: end, candidates: list_of_candidates},
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            context: document.body,
            success: function(tweets){
                var string = '';
                for(var i = 0; i < tweets.length; i++) {
                    string += JSON.stringify(tweets[i]);
                }
                $("#tweets").text(string);
            }});
});