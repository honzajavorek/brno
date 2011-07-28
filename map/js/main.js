/**
 * Main script.
 */

var mapTypes = {};

function init() {
	var brno = new google.maps.LatLng(49.2, 16.616667);

	return new google.maps.Map($('#map-canvas')[0], {
		zoom: 13,
		center: brno,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	});
}

function getKmlUrl(slug) {
    return document.URL + slug + '.kml?nocache=' + (Math.random() * Math.PI * Math.LOG2E);
}

function switchMap(map) {
	slug = $('#controls input:checked').val();
	for (id in mapTypes) {
		if (id == slug) {
			mapTypes[id].setMap(map);
			
		} else {
			mapTypes[id].setMap(null);
		}
	}
}

$(document).ready(function() {
	var map = init();

	$('#controls input').each(function() {
		var slug = $(this).attr('id');
		mapTypes[slug] = new google.maps.KmlLayer(getKmlUrl(slug));
		$(this).click(function() { switchMap(map); });
	});
	
	switchMap(map);
});
