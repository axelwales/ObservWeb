var threatmapGlobals = new Object();

$( "body" ).on("geoLoaded", function(event) {
	setMap(event.json);
});

function setMap(geoJSON) {
	console.log(geoJSON);
	var threatmap = L.map('threatmap', {
		minZoom: 20,
		maxZoom: 23
	});

	/*L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	}).addTo(threatmap);*/

	var style = {
	    "color": "#000000",
	    "weight": 5,
	    "opacity": .8
	};

	threatmap.createPane('buildingPane');
	threatmap.getPane('buildingPane').style.zIndex = 300;

	var engAMap = L.geoJSON(geoJSON, {
		style: style,
		pane: 'buildingPane'
	}).addTo(threatmap);

	var bounds = engAMap.getBounds().pad(.1);
	threatmap.setMaxBounds(engAMap.getBounds().pad(.1));
	threatmap.fitBounds(bounds);

	L.control.scale().addTo(threatmap);

	var cfg = {
		"radius": 10,
	  	"maxOpacity": .8,
	  	valueField: 'threat'
	};
	var heatmapLayer = new HeatmapOverlay(cfg);
	heatmapLayer.addTo(threatmap);

	var heatData = {
	  max: 10,
	  data: []
	};
	heatmapLayer.setData(heatData);

	console.log(threatmap.getPanes());
	threatmap.on('click', function(e) {
		console.log(e);
		heatmapLayer.addData({
			lat: e.latlng.lat,
			lng: e.latlng.lng,
			threat: 10
		});
	});
}

$(function() { 
	$(function() {
	$.ajax({
		url: '/static/map/app-data/EngAFloor3.geojson',
        type: 'GET',
        dataType: 'json',
        error: function(jqXHR, textStatus, errorThrown){
            console.log("Error: " + textStatus);
            console.log(jqXHR);
        },
        success:function(data){
        	threatmapGlobals.mapJSON = data;
        	$( "body" ).trigger({
      		  type:"geoLoaded",
      		  json: threatmapGlobals.mapJSON
      		});
        }
    });
});
});