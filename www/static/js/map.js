var map, dataLayer, neighborhoodLayer, mapboxLayer, satelliteLayer;
var clicked = 0;
var dropdownFocus = 0;//0 is standard. dropdown selection = 1

function updateMap(data, mapsearching, backforward, neighborhood_fit_bounds) {
  tablesorterOptions();

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
        if (neighborhood_fit_bounds === 0) {
          map.fitBounds(dataLayer.getBounds(), {padding: [2, 2]});
        }
      }
    }
  }

  //tableHover(dataLayer);
  //mapHover(dataLayer);
}

function removeNeighborhoodLayer() {
  if (map.hasLayer(neighborhoodLayer)) {
    map.removeLayer(neighborhoodLayer);
  }
}

function updateNeighborhoodLayer(data) {
  if (map.hasLayer(neighborhoodLayer)) {
    map.removeLayer(neighborhoodLayer);
  }

  neighborhoodLayer = L.geoJson(data, {
    // filter: function (feature, layer) {
    //   if (feature.properties) {
    //     // If the property "underConstruction" exists and is true, return false (don't render features under construction)
    //     return feature.properties.underConstruction !== undefined ? !feature.properties.underConstruction : true;
    //   }
    //   return false;
    // },
    style: {
      fillColor: "white",
      fillOpacity: 0,
      color: "#B33125",
      opacity: 1,
      weight: 2,
      dashArray: "5, 5"
    }
    //onEachFeature: onEachFeature
  }).addTo(map);

  map.fitBounds(neighborhoodLayer);
  neighborhoodLayer.bringToBack();
}

function selectedNeighborhood(neighborhood) {
  neighborhood = decodeURIComponent(neighborhood).toUpperCase();
  neighborhood = neighborhood.replace(/ /g, '+');

  // Correct McDonogh from MCDONOGH to McDONOGH:
  neighborhood = neighborhood.replace(/MC/g, 'Mc');

  var url = "http://localhost:5000/static/neighborhood-geojson/" + neighborhood + ".js";
  var static_url = '../../static/neighborhood-geojson/' + neighborhood + '.js';
  var s3_url = 'https://s3-us-west-2.amazonaws.com/lensnola/realestate/neighborhood-geojson/' + neighborhood + '.json';

  $.ajax({
    url: s3_url,
    type: "GET",
    dataType: "json",
    contentType: "application/json; charset=utf-8",
    success: function(data) {
      testGeoJSON = data;
      updateNeighborhoodLayer(data);
    }
  });
}

function loadMapTiles() {
  var stamenLayer = new L.StamenTileLayer("toner-lite", {
    minZoom: 9,
    type: 'png',
    attribution: '<span id="attribution-text">Map data © <a href="http://openstreetmap.org" target="_blank">OpenStreetMap</a>. Tiles by <a href="http://stamen.com" target="_blank">Stamen Design</a>. <a href="http://sos.la.gov/">sos.la.gov</a></span>',
    scrollWheelZoom: false,
    detectRetina: true
  });

  L.mapbox.accessToken = 'pk.eyJ1IjoidHRob3JlbiIsImEiOiJEbnRCdmlrIn0.hX5nW5GQ-J4ayOS-3UQl5w';
  mapboxLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/tthoren.i7m70bek/{z}/{x}/{y}.png', {
    attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Feedback</a>",
    scrollWheelZoom: false,
    detectRetina: true,
    minZoom: 9
    //opacity: 0
  });
  satelliteLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/tthoren.i7m6noin/{z}/{x}/{y}.png', {
    attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Feedback</a>",
    scrollWheelZoom: false,
    detectRetina: true,
    minZoom: 9
  });

  var tileTimeout;

  function switchToStamen() {
    clearTimeout(tileTimeout);
    // console.error('Not finding Stamen tiles. Switching to OSM tiles...');
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
    var div = L.DomUtil.create('div', 'logo');
    div.innerHTML = "<img src='https://s3-us-west-2.amazonaws.com/lensnola/realestate/css/images/lens-logo-retina.png' alt='Lens logo' width='100'>";
    return div;
  };
  logo.addTo(map);
}

function createMap() {
  map = new L.Map("map", {
    minZoom: 9,
    maxZoom: 18,
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

function clickFeature(e) {
  /*
  Clicked on a feature, such as a precinct or parish.
  */

  instrument_no = e.target.feature.properties.instrument_no;
  window.location.href = "/realestate/sale/" + instrument_no;
}

function highlightFeature(e) {
  /*
  Hover on a feature, such as a precinct or parish.
  */

  var layer = e.target;
  var feature = e.target.feature;

  if (clicked === 1) {
    return;
  }
  var html;
  html = "<div class='popup'>" +
    "<strong>Date: </strong>" + feature.properties.document_date + "<br>" +
    "<strong>Amount: </strong>" + feature.properties.amount + "<br>" +
    "<strong>Address: </strong>" + (feature.properties.address).trunc(150) + "<br>" +
    "<strong>Location info: </strong>" + (feature.properties.location_info).trunc(150) + "<br>" +
    "<strong>Sellers: </strong>" + feature.properties.sellers + "<br>" +
    "<strong>Buyers: </strong>" + feature.properties.buyers + "<br>" +
    "<br><a><em>Click marker for more information.</em></a>" +
  "</div>";
  if (!L.Browser.ie && !L.Browser.opera) { // Fix for IE and Opera
    layer.bringToFront();
  }
  $('#tooltip').html(html);
  var tooltip_height = $('#tooltip').outerHeight(true);
  $('#tooltip').css({"display": "block",
    "left": (
      e.containerPoint.x < (map._size.x / 3) ?
        e.originalEvent.pageX :
        (e.containerPoint.x >= (map._size.x / 3) && e.containerPoint.x < (2 * map._size.x / 3) ?
          e.originalEvent.pageX - 235 / 2 :
          e.originalEvent.pageX - 235
        )
    ),
    "top": (
      e.containerPoint.y < (map._size.y / 2) ?
        e.originalEvent.pageY + 20 :
        e.originalEvent.pageY - tooltip_height - 20
    )
  });
}

function resetHighlight(e) {
  /*
  Clicked on a feature, such as a precinct or parish.
  */

  if (clicked === 1) {
    return;
  }
  $('#tooltip').css({"display": "none"});
}

function resetClicked() {
  /*
  Ensure tooltip's 'clicked' variable is equal to 0.
  */

  if (clicked === 1) {
    clicked = 0;
    resetHighlight();
  }
}

function addDataToMap(data) {
  var dataLayer2 = L.geoJson(data, {
    onEachFeature: onEachFeature,
    pointToLayer: function (feature, layer) {
      return L.circleMarker(layer, {
        radius: 10,
        color: 'white',
        opacity: 0.8,
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
      layer.setStyle({radius: 10, color: 'white', opacity: 1.0, fillColor: '#B33125', fillOpacity: 1.0});
      layer.bringToFront();
    });
    layer.on('mouseout', function (event) {
      layer.setStyle({radius: 10, color: 'white', opacity: 0.8, fillColor: '#B33125', fillOpacity: 0.5});
    });
  });
}

function showFooterOrNot(data) {
  for (var i = 0; i < data.features.length; i++) {
    if (data.features[i].properties.location_publish === false) {
      // Show asterisk note
      document.getElementById('asterisk-note').style.display = 'block';
    } else if (data.features[i].properties.permanent_flag === false) {
      // Show cross note
      document.getElementById('cross-note').style.display = 'block';
    }
  }
}

// https://stackoverflow.com/a/901144
function getParameterByName(name, url) {
  if (!url) url = window.location.href;
  name = name.replace(/[\[\]]/g, "\\$&");
  var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function initialMapFunction(data) {
  // Not sure what this is
  tablesorterOptions();

  createMap();
  loadMapTiles();
  addLensLogoToMap();
  addDataToMap(data);
  showFooterOrNot(data);

  var nbhd_text;

  if (window.location.search.substring(0).match(/nbhd\=(.*)/i) !== null) {
    // nbhd_text = decodeURIComponent(window.location.search.substring(0).match(/nbhd\=(.*)/i)[1]);
    nbhd_text = getParameterByName('nbhd');
  }

  if (Object.keys(dataLayer._layers).length === 0) { //if there aren't any points on the map
    map.setView([29.996953, -90.048277], 11);
  } else {
    if (typeof nbhd_text === 'undefined') {
      map.fitBounds(dataLayer.getBounds(), {paddingTopLeft: [2, 2], paddingBottomRight: [2, 2]});
    } else {
      selectedNeighborhood(nbhd_text);
    }
  }

  //tableHover(dataLayer);
  //mapHover(dataLayer);

  map.on('moveend', function (e) {
    if (document.getElementById("map-button").checked === true) {
      mapSearching();
    }
  });
  map.on('click', function(e) {
    resetClicked();
  });

  // todo for satellite layer:
  map.on('baselayerchange', function(event) {
    // console.log('baselayerchange');
    if (map.hasLayer(satelliteLayer)) {
      // console.log('satelliteLayer');
      $('.logo').css({
        'background-color': 'rgba(255, 255, 255, 0.5)',
        'box-shadow': '0px 0px 7px 7px rgba(255, 255, 255, 0.5)'
      });
      $('.leaflet-control-attribution').css({"background-color": 'rgba(255, 255, 255, 0.75)'});
    }

    if (map.hasLayer(mapboxLayer)) {
      // console.log('mapboxLayer');
      $('.logo').css({
        'background-color': 'rgba(255, 255, 255, 0)',
        'box-shadow': '0px 0px 0px 0px rgba(255, 255, 255, 0)'
      });
      $('.leaflet-control-attribution').css({"background-color": 'rgba(255, 255, 255, 0.25)'});
    }
  });
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

$(document).on('mouseenter', "#myTable tbody tr td", function (event) {
  var parent = $(event.target).parent().attr('id');
  dataLayer.eachLayer(function (layer) {
    if (layer.feature.properties.instrument_no === parent) {
      layer.setStyle({radius: 10, color: 'white', opacity: 1.0, fillColor: '#B33125', fillOpacity: 1.0});
      layer.bringToFront();
    }
    if (layer.feature.properties.instrument_no !== parent) {
      layer.setStyle({radius: 10, color: 'white', opacity: 1.0, fillColor: '#B33125', fillOpacity: 0.5});
    }
  });
});
$(document).on('mouseleave', "#myTable tbody tr td", function (event) {
  var parent = $(event.target).parent().attr('id');
  dataLayer.eachLayer(function (layer) {
    if (layer.feature.properties.instrument_no === parent) {
      layer.setStyle({radius: 10, color: 'white', opacity: 0.8, fillColor: '#B33125', fillOpacity: 0.5});
    }
    if (layer.feature.properties.instrument_no !== parent) {
      layer.setStyle({radius: 10, color: 'white', opacity: 0.8, fillColor: '#B33125', fillOpacity: 0.5});
    }
  });
});
