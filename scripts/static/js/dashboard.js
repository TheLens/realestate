var dataLayer;

function initializeMap(loop_index, latitude, longitude, location_publish, detail_publish, amount, document_date, document_recorded) {
  var map_container = "map_" + loop_index;
  //console.log('map_container: ', map_container);
  //console.log('location_publish: ', location_publish);
  var map = new L.Map(map_container, {
    minZoom: 13,
    maxZoom: 20,
    scrollWheelZoom: false,
    fadeAnimation: false,
    zoomControl: false,
    center: [latitude, longitude],
    zoom: 17
  });

  console.log('amount:', amount);

  //Change input borders depending on good or not
  if (location_publish === 'No') {
    document.getElementById('location_publish_' + loop_index).style.border = "2px solid red";
    document.getElementById('location_publish_' + loop_index).style.boxShadow = "0 0 10px red";
  } else {
    document.getElementById('location_publish_' + loop_index).style.border = "2px solid green";
    document.getElementById('location_publish_' + loop_index).style.boxShadow = "0 0 10px green";
  }

  if (detail_publish === 'No') {
    document.getElementById('detail_publish_' + loop_index).style.border = "2px solid red";
    document.getElementById('detail_publish_' + loop_index).style.boxShadow = "0 0 10px red";
  } else {
    document.getElementById('detail_publish_' + loop_index).style.border = "2px solid green";
    document.getElementById('detail_publish_' + loop_index).style.boxShadow = "0 0 10px green";
  }

  if (amount === '$0' || parseInt($('#amount_1').val().replace(/[$,]/g, ''), 10) >= 20000000) {
    document.getElementById('amount_' + loop_index).style.border = "2px solid red";
    document.getElementById('amount_' + loop_index).style.boxShadow = "0 0 10px red";
  }

  if (document_date === 'None') {
    document.getElementById('document_date_' + loop_index).style.border = "2px solid red";
    document.getElementById('document_date_' + loop_index).style.boxShadow = "0 0 10px red";
  }

  if (document_recorded === 'None') {
    document.getElementById('document_recorded_' + loop_index).style.border = "2px solid red";
    document.getElementById('document_recorded_' + loop_index).style.boxShadow = "0 0 10px red";
  }

  L.circleMarker([latitude, longitude], {
    radius: 10,
    color: location_publish === 'Yes' ? 'green' : '#B33125',
    fillColor: location_publish === 'Yes' ? 'green' : '#B33125',
    fillOpacity: 0.5
  }).addTo(map);

  // Add zoom control to top left corner of the map.
  L.control.zoom({position: 'topleft'}).addTo(map);

  L.mapbox.accessToken = 'pk.eyJ1IjoidHRob3JlbiIsImEiOiJEbnRCdmlrIn0.hX5nW5GQ-J4ayOS-3UQl5w';
  var mapboxLayer = L.tileLayer('https://{s}.tiles.mapbox.com/v3/tthoren.i7m70bek/{z}/{x}/{y}.png', {
    attribution: "<a href='https://www.mapbox.com/about/maps/' target='_blank'>&copy; Mapbox &copy; OpenStreetMap</a> <a class='mapbox-improve-map' href='https://www.mapbox.com/map-feedback/' target='_blank'>Feedback</a>",
    scrollWheelZoom: false,
    detectRetina: true,
    minZoom: 6
  });
  map.addLayer(mapboxLayer);

  //console.log('map:', map);

  return map;
}

function addDataToMap(map, neighborhoods, squares) {
  /*
  var neighborhoodsTopoLayer = topojson.feature(neighborhoods, neighborhoods.objects.neighborhoods);
  var neighborhoodsLayer = L.geoJson(neighborhoodsTopoLayer, {
    filter: function (feature, layer) {
      if (feature.properties) {
        // If the property "underConstruction" exists and is true, return false (don't render features under construction)
        return feature.properties.underConstruction !== undefined ? !feature.properties.underConstruction : true;
      }
      return false;
    },
    style: {
      fillColor: "#000",
      opacity: 1.0,
      color: "white",
      fillOpacity: 0.5,
      weight: 0.7,
      fill: true,
      stroke: true
    }
  }).addTo(map);
  */

  /*
  var squaresTopoLayer = topojson.feature(squares, squares.objects.squares);
  var squaresLayer = L.geoJson(squaresTopoLayer, {
    filter: function (feature, layer) {
      if (feature.properties) {
        // If the property "underConstruction" exists and is true, return false (don't render features under construction)
        return feature.properties.underConstruction !== undefined ? !feature.properties.underConstruction : true;
      }
      return false;
    },
    style: {
      fillColor: "#000",
      opacity: 1.0,
      color: "white",
      fillOpacity: 0.5,
      weight: 0.7,
      fill: true,
      stroke: true
    },
    onEachFeature: function (feature, layer) {
      layer.on('click', function () {
        console.log('feature:', feature);
        console.log('layer:', layer);
        layer.bindPopup('<div>District: ' + feature.properties.dist + '<br>Square: ' + feature.properties.square + '</div>').openPopup();
      });
    }
  });//.addTo(map);
  */

}

function buildQueryString(data) {
  var map_query_string = '?';

  if (data.name_address !== '') {
    map_query_string = map_query_string + "q=" + data.name_address;
  }

  if (data.amountlow !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "a1=" + data.amountlow;
  }

  if (data.amounthigh !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "a2=" + data.amounthigh;
  }

  if (data.begindate !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "d1=" + data.begindate;
  }

  if (data.enddate !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "d2=" + data.enddate;
  }

  if (map_query_string == '?') {
    map_query_string = "?q=&a1=&a2=&d1=&d2=";
  }

  return map_query_string;
}

function doPostBack(data) {
  console.log('doPostBack');
  var searchrequest = JSON.stringify(data);
  //var query_string = buildQueryString(data);
  $.ajax({
    url: "/realestate/dashboard",
    type: "POST",
    data: searchrequest,
    contentType: "application/json; charset=utf-8",
    success: function (info) {
      console.log(info);
      //window.history.pushState(null,'hi','search' + query_string);

      // $("#map-table-wrapper").html(info.template1);
      // $("#map-table-wrapper").trigger("updateAll");
      // document.getElementById('map-table-wrapper').style.display = 'block';
      // document.getElementById('foot').style.display = 'block';

      // initialMapFunction(info.jsdata);
    }
  });
}

function preparePOST(loop_index) {
  //$("body").addClass("loading");
  console.log('loop_index:', loop_index);

  var data = {};
  data.instrument_no = $('#instrument_no_' + loop_index).text();
  data.detail_publish = $('#detail_publish_' + loop_index).val();
  data.location_publish = $('#location_publish_' + loop_index).val();
  data.document_date = $('#document_date_' + loop_index).val();

  data.amount = $('#amount_' + loop_index).val();
  data.amount = data.amount.replace(/[,$]/g, '');

  data.address = $('#address_' + loop_index).val();
  data.location_info = $('#location_info_' + loop_index).val();
  data.sellers = $('#sellers_' + loop_index).val();
  data.buyers = $('#buyers_' + loop_index).val();
  data.document_recorded = $('#document_recorded_' + loop_index).val();
  data.latitude = $('#latitude_' + loop_index).val();
  data.longitude = $('#longitude_' + loop_index).val();
  data.zip_code = $('#zip_code_' + loop_index).val();
  data.neighborhood = $('#neighborhood_' + loop_index).val();

  console.log('amount: ', data.amount);
  console.log('amount type: ', typeof data.amount);

  console.log('instrument no: ', data.instrument_no);
  console.log('data:', data);

  return data;
}

// function showPreview(data) {
//   console.log(data.instrument_no);
//   document.getElementById('preview_instrument_no').innerHTML = data.instrument_no;
//   document.getElementById('preview').style.display = "block";
// }

$(document).on("click", '.searchButton', function (e) {
  console.log('e:', e);
  var loop_index = $(event.target).attr('id');
  console.log('loop_index:', loop_index);

  var data = preparePOST(loop_index);

  //Prompt preview and double-check
  //showPreview(data);

  doPostBack(data);
  document.getElementById('preview').style.display = 'none';

  /*
  $(document).on("click", '.searchButtonTrue', function () {
    doPostBack(data);

    //todo: update page here.

    document.getElementById('preview').style.display = 'none';
  });
  */

});

// $(document).on("click", '.closeDiv', function () {
//   document.getElementById('preview').style.display = 'none';
// });

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

function initialFunction(number_of_indexes, jsrows) {
  //console.log('Number of indexes:', number_of_indexes);
  //console.log("jsrows:", jsrows);
  for (var i = 1; i < number_of_indexes + 1; i++) {
    console.log('Index: ', i);
    var map = initializeMap(i, jsrows[i - 1].latitude, jsrows[i - 1].longitude, jsrows[i - 1].location_publish, jsrows[i - 1].detail_publish, jsrows[i - 1].amount, jsrows[i - 1].document_date, jsrows[i - 1].document_recorded);
    //addDataToMap(map, neighborhoods, squares);
  }
}

