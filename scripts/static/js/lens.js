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
    attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Improve this map</a>",
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
    maxZoom: 16,
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

function resetAmounts(amountlow, amounthigh) {
  if (amountlow === 'Please enter a valid amount range.') {
    amountlow = '';
    document.getElementById('amount1').value = "";
  }
  if (amounthigh === 'Please enter a valid amount range.') {
    amounthigh = '';
    document.getElementById('amount2').value = "";
  }
  return {low: amountlow, high: amounthigh};
}

function resetDates(begindate, enddate) {
  if (begindate === 'Please enter a valid date format.' || begindate === 'Please enter a valid date range.') {
    begindate = '';
    document.getElementById('date1').value = "";
  }
  if (enddate === 'Please enter a valid date format.' || enddate === 'Please enter a valid date range.') {
    enddate = '';
    document.getElementById('date2').value = "";
  }
  return {begin: begindate, end: enddate};
}

function checkAmounts(amountlow, amounthigh) {
  if (isValidAmountRange(amountlow, amounthigh) === false) {
    //$("body").removeClass("loading");
    console.log('false');
    document.getElementById('amount1').value = "Please enter a valid amount range.";
    document.getElementById('amount2').value = "Please enter a valid amount range.";
    return false;
  }
}

function checkDates(begindate, enddate) {
  var tf;
  if (isValidDate(begindate) === false) {
    //$("body").removeClass("loading");
    document.getElementById('date1').value = "Please enter a valid date format.";
    tf = false;
  }
  if (isValidDate(enddate) === false) {
    //$("body").removeClass("loading");
    document.getElementById('date2').value = "Please enter a valid date format.";
    tf = false;
  }
  if (isValidDateRange(begindate, enddate) === false) {
    document.getElementById('date1').value = "Please enter a valid date range.";
    document.getElementById('date2').value = "Please enter a valid date range.";
    tf = false;
  }
  return tf;
}

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

$(document).on("click", '.searchButton', function () {
  document.getElementById('search-button').innerHTML = '';//Remove "Search" button

  var data = preparePOST();

  if (data === false) {
    return;
  }

  if (typeof map !== 'undefined') { // map has been initialized
    var bounds = map.getBounds(); // Why get bounds if "Search" hit with map filtering turned off?
    data.bounds = bounds;
    var mapbuttonstate = document.getElementById("mapButton").checked;
    data.mapbuttonstate = mapbuttonstate;

    var page = $('#table-wrapper').attr('data-page');
    var totalpages = $('#table-wrapper').attr('data-totalpages');
    data.page = page;
    data.totalpages = totalpages;
    data.direction = 'none';

    var maprequest = JSON.stringify(data);
    $.ajax({
      url: "/realestate/mapsearch",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        $("#table-footer-wrapper").html(info.tabletemplate);
        $("#table-footer-wrapper").trigger("updateAll");
        $("#results-found").html(info.resultstemplate);
        updateMap(info.jsdata, 0);
      }
    });
  } else { //initial search without map initialized yet
    console.log('data.name_address: ', data.name_address);
    var searchrequest = JSON.stringify(data);
    $.ajax({
      url: "/realestate/search/" + data.name_address,
      //url: "/realestate/search",
      type: "POST",
      data: searchrequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        $("#map-table-wrapper").html(info.template1);
        $("#map-table-wrapper").trigger("updateAll");
        $("#foot").html(info.template2);
        document.getElementById('map-table-wrapper').style.display = 'block';
        document.getElementById('foot').style.display = 'block';
        initialMapFunction(info.jsdata);
      }
    });
  }
});

$("body").on("click", ".pageforward", function () {
  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  if (page !== totalpages) {
    //$("body").addClass("loading");

    var data = preparePOST();

    data.bounds = map.getBounds(); // Why get bounds if "Search" hit with map filtering turned off?;

    var mapbuttonstate = document.getElementById("mapButton").checked;
    data.mapbuttonstate = mapbuttonstate;

    //Find pagination details
    var pagelength = $('#table-wrapper').attr('data-pagelength');
    data.page = page;
    data.totalpages = totalpages;
    data.pagelength = pagelength;
    data.direction = 'forward';

    var maprequest = JSON.stringify(data);
    $.ajax({
      url: "/realestate/mapsearch",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        $("#table-footer-wrapper").html(info.tabletemplate);
        $("#table-footer-wrapper").trigger("updateAll");
        $("#results-found").html(info.resultstemplate);
        updateMap(info.jsdata, 0, 1);
      }
    });
  }
});

function preparePOST() {
  //$("body").addClass("loading");

  var name_address = encodeURIComponent($('#name_address_box').val());
  var amountlow1 = $('#amount1').val();
  var amounthigh1 = $('#amount2').val();
  var amountlow = amountlow1.replace(/[,$]/g, '');
  var amounthigh = amounthigh1.replace(/[,$]/g, '');
  var begindate = $('#date1').val();
  var enddate = $('#date2').val();

  var data = {};

  var amounts = resetAmounts(amountlow, amounthigh);
  amountlow = amounts['low'];
  amounthigh = amounts['high'];

  if (checkAmounts(amountlow, amounthigh) === false) {
    data = false;
    return data;
  }

  var dates = resetDates(begindate, enddate);
  begindate = dates['begin'];
  enddate = dates['end'];

  if (checkDates(begindate, enddate) === false) {
    data = false;
    return data;
  }

  data.name_address = name_address;
  data.amountlow = amountlow;
  data.amounthigh = amounthigh;
  data.begindate = begindate;
  data.enddate = enddate;

  return data;
}

$("body").on("click", ".pageback", function () {
  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  if (page !== "1") {
    //$("body").addClass("loading");

    var data = preparePOST();

    data.bounds = map.getBounds(); // Why get bounds if "Search" hit with map filtering turned off?

    var mapbuttonstate = document.getElementById("mapButton").checked;
    data.mapbuttonstate = mapbuttonstate;

    //Find pagination details

    page = $('#table-wrapper').attr('data-page');
    totalpages = $('#table-wrapper').attr('data-totalpages');
    var pagelength = $('#table-wrapper').attr('data-pagelength');
    data.page = page;
    data.totalpages = totalpages;
    data.pagelength = pagelength;
    data.direction = 'back';

    var maprequest = JSON.stringify(data);

    $.ajax({
      url: "/realestate/mapsearch",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        $("#table-footer-wrapper").html(info.tabletemplate);
        $("#table-footer-wrapper").trigger("updateAll");
        $("#results-found").html(info.resultstemplate);
        updateMap(info.jsdata, 0, 1);
      }
    });
  }
});

$("#advanced-search").on("click", function () {
  if ($('#filters').css('display') === 'none') {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search</a>';
  }
  else {
    document.getElementById('filters').style.display = 'none';
    document.getElementById('advanced-search').innerHTML = '<a>Show advanced search</a>';
  }
});


function formatCurrency(number) {
  var n = number.split('').reverse().join("");
  var n2 = n.replace(/\d\d\d(?!$)/g, "$&,");
  return '$' + n2.split('').reverse().join('');
}

$('.currency').on('input', function () {
  $(this).val(formatCurrency(this.value.replace(/[,$]/g, '')));
}).on('keypress', function (e) {
  if (!$.isNumeric(String.fromCharCode(e.which)) && (e.which !== 8)) {
    e.preventDefault();
  }
});

$(document.body).keyup(function (event) {
  if (event.which === 13) {
    $(".searchButton").click();
  }
});

$( "#date1" ).datepicker({
    minDate: new Date(2014, 1, 18)
  });
$( "#date2" ).datepicker();

if ($(window).width() < 500) {
  $('#name_address_box').attr('placeholder','Enter buyer, seller, address, zip');
  $('#date1').attr('placeholder','');
  $('#date2').attr('placeholder','');
}


function isValidDate(dateString) {
  if (dateString === '') {
    return true;
  }
  // First check for the pattern
  if (!/^\d{2}\/\d{2}\/\d{4}$/.test(dateString)) {
    return false;
  }
  // Parse the date parts to integers
  var parts = dateString.split("/");
  var day = parseInt(parts[1], 10);
  var month = parseInt(parts[0], 10);
  var year = parseInt(parts[2], 10);
  // Check the ranges of month and year
  if (month === 0 || month > 12) {
    return false;
  }
  var monthLength = [ 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ];
  // Adjust for leap years
  if (year % 400 === 0 || (year % 100 !== 0 && year % 4 === 0)) {
    monthLength[1] = 29;
  }
  // Check the range of the day
  if (day > monthLength[month - 1]) {
    return false;
  }
  return true;
}

function isValidDateRange(begindate, enddate) {
  var parts1 = begindate.split("/");
  var day1 = parseInt(parts1[1], 10);
  var month1 = parseInt(parts1[0], 10);
  var year1 = parseInt(parts1[2], 10);

  var parts2 = enddate.split("/");
  var day2 = parseInt(parts2[1], 10);
  var month2 = parseInt(parts2[0], 10);
  var year2 = parseInt(parts2[2], 10);

  if (year2 <= year1) {
    if (month2 <= month1) {
      if (day2 < day1) {
        return false;
      }
    }
  }
  return true;
}

function isValidAmountRange(amount1, amount2) {
  amount1 = parseInt(amount1, 10);
  amount2 = parseInt(amount2, 10);
  if (isNaN(amount1) === true || isNaN(amount2) === true) {
    return true;
  }
  if (amount1 > amount2) {
    return false;
  }
}

document.onload = checkForChanges();

function checkForChanges()
{
  if ($('button.t402-elided').length) {
    setTimeout(checkForChanges, 2000);
  }
  else {
    $('button').addClass('searchButton');
  }
}
