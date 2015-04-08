var map, dataLayer;
var clicked = 0;

function loadMapTiles() {
  var stamenLayer = new L.StamenTileLayer("toner-lite", {
    minZoom: 9,
    type: 'png',
    attribution: '<span id="attribution-text">Map data © <a href="http://openstreetmap.org" target="_blank">OpenStreetMap</a>. Tiles by <a href="http://stamen.com" target="_blank">Stamen Design</a>. <a href="http://sos.la.gov/">sos.la.gov</a></span>',
    scrollWheelZoom: false,
    detectRetina: true
  });

  L.mapbox.accessToken = 'pk.eyJ1IjoidHRob3JlbiIsImEiOiJEbnRCdmlrIn0.hX5nW5GQ-J4ayOS-3UQl5w';
  var mapboxLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/tthoren.i7m70bek/{z}/{x}/{y}.png', {
    attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Feedback</a>",
    scrollWheelZoom: false,
    detectRetina: true,
    minZoom: 9
  });
  var satelliteLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/tthoren.i7m6noin/{z}/{x}/{y}.png', {
    attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Feedback</a>",
    scrollWheelZoom: false,
    detectRetina: true,
    minZoom: 9
  });

  var tileTimeout;

  function switchToStamen() {
    clearTimeout(tileTimeout);
    console.error('Not finding Stamen tiles. Switching to OSM tiles...');
    map.removeLayer(mapboxLayer);
    map.addLayer(stamenLayer);
  }

  var baseMaps = {
    "Color": mapboxLayer,
    "Satellite": satelliteLayer
  };

  map.addLayer(mapboxLayer);
  L.control.layers(baseMaps).addTo(map);

  tileTimeout = setTimeout(switchToStamen, 10000);

  mapboxLayer.on('tileload', function(e) {
    clearTimeout(tileTimeout);
  });
}

function addLensLogoToMap() {
  var logo = L.control({position: 'bottomleft'});
  logo.onAdd = function () {
    var div = L.DomUtil.create('div');
    div.innerHTML = "<img src='https://s3-us-west-2.amazonaws.com/lensnola/land-records/css/images/lens-logo-retina.png' alt='Lens logo' width='100' >";
    return div;
  };
  logo.addTo(map);
}

function createMap() {
  map = new L.Map("map", {
    minZoom: 9,
    maxZoom: 16,
    scrollWheelZoom: false,
    fadeAnimation: false,
    zoomControl: false
  });

  // Add zoom control to top left corner of the map.
  L.control.zoom({position: 'topleft'}).addTo(map);
}

function onEachFeature(feature, layer) {
  /*
  Leaflet functions to be assigned to each feature on a given layer.
  */
  layer.on({
    click: clickFeature,
    mouseover: highlightFeature,
    mouseout: resetHighlight
  });
}

function addDataToMap(data) {
  var dataLayer2 = L.geoJson(data, {
    //onEachFeature: onEachFeature,
    pointToLayer: function (feature, layer) {
      return L.circleMarker(layer, {
        radius: 10,
        color: 'white',
        opacity: 1.0,
        fillColor: '#B33125',
        fillOpacity: 1.0
      });
    }
  });

  if (map.hasLayer(dataLayer)) {
    map.removeLayer(dataLayer);
  }
  dataLayer = dataLayer2;
  map.addLayer(dataLayer);

  // dataLayer.eachLayer(function (layer) {
  //   layer.on('mouseover', function (event) {
  //     layer.setStyle({radius: 10, color: 'white', opacity: 1.0, fillColor: '#B33125', fillOpacity: 1.0});
  //     layer.bringToFront();
  //   });
  //   layer.on('mouseout', function (event) {
  //     layer.setStyle({radius: 10, color: 'white', opacity: 0.8, fillColor: '#B33125', fillOpacity: 0.5});
  //   });
  // });

  //logo.addTo(map);
}

function initialMapFunction(data) {

  createMap();
  loadMapTiles();
  addLensLogoToMap();
  addDataToMap(data);

  if (Object.keys(dataLayer._layers).length === 0) { //if there aren't any points on the map
    map.setView([29.996953, -90.048277], 11);
  } else {
    map.fitBounds(dataLayer.getBounds());
  }
  
  //tableHover(dataLayer);
  //mapHover(dataLayer);
}

function mapHover(dataLayer) {
  dataLayer.eachLayer(function (layer) {
    layer.on('mouseover', function (event) {
      layer.setStyle({radius: 10, color: 'white', opacity: 1.0, fillColor: '#B33125', fillOpacity: 1.0});
      layer.bringToFront();
    });
    layer.on('mouseout', function (event) {
      layer.setStyle({radius: 10, color: 'white', opacity: 0.8, fillColor: '#B33125', fillOpacity: 0.5});
    });
  });
}
