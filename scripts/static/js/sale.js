var map, dataLayer;

function tablesorterThing() {
  // Not sure about stuff below
  $("#myTable thead th:eq(0)").data("sorter", false);
  $("#myTable thead th:eq(1)").data("sorter", false);
  $("#myTable thead th:eq(2)").data("sorter", false);
  $("#myTable thead th:eq(3)").data("sorter", false);
  $("#myTable thead th:eq(4)").data("sorter", false);
  $("#myTable thead th:eq(5)").data("sorter", false);
  $("#myTable").tablesorter({widthFixed: true});
}

function updateMap(data, mapsearching, backforward) {
  // Not sure about stuff below
  tablesorterThing();

  var center = map.getCenter();
  var zoom = map.getZoom();

  addDataToMap(data);

  if (mapsearching === 1) {
    // If box is checked yes, don't alter user's view 
    map.setView(center, zoom);
  } else if (mapsearching === 0) {
    if (backforward !== 1) {
      if (Object.keys(dataLayer._layers).length === 0) { //if there aren't any points on the map
        map.setView(center, zoom);
      } else {
        map.fitBounds(dataLayer.getBounds());
      }
    }
  }
  //$("body").removeClass("loading");
  //tableHover(dataLayer);
  //mapHover(dataLayer);
}

function loadMapTiles() {
  var stamenLayer = new L.StamenTileLayer("toner-lite", {
    minZoom: 6,
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
    minZoom: 6
  });

  var tileTimeout;

  function switchToStamen() {
    clearTimeout(tileTimeout);
    console.error('Not finding Stamen tiles. Switching to OSM tiles...');
    map.removeLayer(mapboxLayer);
    map.addLayer(stamenLayer);
  }

  //map.addLayer(osm);
  map.addLayer(mapboxLayer);
  tileTimeout = setTimeout(switchToStamen, 10000);

  mapboxLayer.on('tileload', function(e) {
    clearTimeout(tileTimeout);
  });
}

function addLensLogoToMap() {
  var logo = L.control({position: 'bottomleft'});
  logo.onAdd = function () {
    var div = L.DomUtil.create('div');
    div.innerHTML = "<img src='https://s3-us-west-2.amazonaws.com/lensnola/land-records/css/images/lens-logo.png' alt='Lens logo' >";
    return div;
  };
  logo.addTo(map);
}

function createMap() {
  map = new L.Map("map", {
    minZoom: 6,
    maxZoom: 15,
    scrollWheelZoom: false,
    fadeAnimation: false,
    zoomControl: false
  });

  // Add zoom control to top left corner of the map.
  L.control.zoom({position: 'topleft'}).addTo(map);
}

function addDataToMap(data) {
  var dataLayer2 = L.geoJson(data, {
    onEachFeature: function (feature, layer) {
      layer.on('click', function () {
        layer.bindPopup("<div class='popup'><p><strong>Date: </strong>" + feature.properties.document_date + "<br><strong>Amount: </strong>" + feature.properties.amount + "<br><strong>Location: </strong>" + feature.properties.location + "<br><strong>Sellers: </strong>" + feature.properties.sellers + "<br><strong>Buyers: </strong>" + feature.properties.buyers + "<br><strong>Instrument number: </strong>" + feature.properties.instrument_no + "<br><strong></p></div>", {'maxWidth': '250', 'maxHeight': '300', 'autoPanPaddingTopLeft': [40, 12]}).openPopup();
      });
    },
    pointToLayer: function (feature, layer) {
      return L.circleMarker(layer, {
        radius: 10,
        color: '#B33125',
        fillColor: '#B33125',
        fillOpacity: 0.5
      });
    }
  });

  if (map.hasLayer(dataLayer)) {
    map.removeLayer(dataLayer);
  }
  dataLayer = dataLayer2;
  map.addLayer(dataLayer);

  dataLayer.eachLayer(function (layer) {
    layer.on('mouseover', function (event) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 1.0});
      layer.bringToFront();
    });
    layer.on('mouseout', function (event) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 0.5});
    });
  });

  //logo.addTo(map);
  //$("body").removeClass("loading");
}

function initialMapFunction(data) {
  // Not sure what this is
  tablesorterThing();

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

  map.on('moveend', function (e) {
    if (document.getElementById("mapButton").checked === true) {
      //$("body").addClass("loading");
      mapSearching();
    }
  });
}

function mapHover(dataLayer) {
  dataLayer.eachLayer(function (layer) {
    layer.on('mouseover', function (event) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 1.0});
      layer.bringToFront();
    });
    layer.on('mouseout', function (event) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 0.5});
    });
  });
}

$(document).on('click', "#myTable tbody tr", function (event) {
  var parent = $(event.target).parent().attr('id');
  dataLayer.eachLayer(function (layer) {
    if (layer.feature.properties.instrument_no === parent) {
      if (layer._map.hasLayer(layer._popup)) {
        layer.closePopup();
      } else {
        layer.bindPopup("<div class='popup'><p><strong>Date: </strong>" + layer.feature.properties.document_date + "<br><strong>Amount: </strong>" + layer.feature.properties.amount + "<br><strong>Location: </strong>" + layer.feature.properties.location + "<br><strong>Sellers: </strong>" + layer.feature.properties.sellers + "<br><strong>Buyers: </strong>" + layer.feature.properties.buyers + "<br><strong>Instrument number: </strong>" + layer.feature.properties.instrument_no + "<br><strong></p></div>", {'maxWidth': '250', 'maxHeight': '300', 'autoPanPaddingTopLeft': [40, 12]}).openPopup();
      }
    }
  });
});

$(document).on('mouseenter', "#myTable tbody tr td", function (event) {
  var parent = $(event.target).parent().attr('id');
  dataLayer.eachLayer(function (layer) {
    if (layer.feature.properties.instrument_no === parent) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 1.0});
      layer.bringToFront();
    }
    if (layer.feature.properties.instrument_no !== parent) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 0.5});
    }
  });
});
$(document).on('mouseleave', "#myTable tbody tr td", function (event) {
  var parent = $(event.target).parent().attr('id');
  dataLayer.eachLayer(function (layer) {
    if (layer.feature.properties.instrument_no === parent) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 0.5});
    }
    if (layer.feature.properties.instrument_no !== parent) {
      layer.setStyle({radius: 10, color: '#B33125', colorOpacity: 1.0, fillColor: '#B33125', fillOpacity: 0.5});
    }
  });
});

function mapSearching() {
  var data = preparePOST();

  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  data.page = page;
  data.totalpages = totalpages;
  data.direction = 'none';

  data.bounds = map.getBounds();
  data.mapbuttonstate = true;

  var request = JSON.stringify(data);

  $.ajax({
    url: "/realestate/mapsearch",
    type: "POST",
    data: request,
    contentType: "application/json; charset=utf-8",
    success: function (info) {
      $("#table-footer-wrapper").html(info.tabletemplate);
      $("#table-footer-wrapper").trigger("updateAll");
      $("#results-found").html(info.resultstemplate);
      updateMap(info.jsdata, 1);
    }
  });
}
