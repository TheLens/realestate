var map, dataLayer;
var clicked = 0;
var dropdownFocus = 0;//0 is standard. dropdown selection = 1

function tablesorterOptions() {
  // Not sure about stuff below
  $("#myTable thead th:eq(0)").data("sorter", false);
  $("#myTable thead th:eq(1)").data("sorter", false);
  $("#myTable thead th:eq(2)").data("sorter", false);
  $("#myTable thead th:eq(3)").data("sorter", false);
  $("#myTable thead th:eq(4)").data("sorter", false);
  $("#myTable thead th:eq(5)").data("sorter", false);
  $("#myTable").tablesorter({widthFixed: false});
}

function mapSearching() {
  var nbhd_text, zip_text;

  if (window.location.search.substring(0).match(/nbhd\=(.*)/i) !== null) {
    nbhd_text = decodeURIComponent(window.location.search.substring(0).match(/nbhd\=(.*)/i)[1]);
    //console.log('nbhd_text:', nbhd_text);
  }

  if (window.location.search.substring(0).match(/zip\=(.*)/i) !== null) {
    zip_text = window.location.search.substring(0).match(/zip\=(.*)/i)[1];
  }

  // If search input bar unchanged (nbhd in URL matches search input text), delete.
  if (document.getElementById('name_address_box').value.trim() === nbhd_text || document.getElementById('name_address_box').value.trim() === zip_text) {
    document.getElementById('name_address_box').value = '';
  }

  if (document.getElementById('neighborhood').value !== '') {
    document.getElementById('neighborhood').value = '';
  }

  if (document.getElementById('zip_code').value !== '') {
    document.getElementById('zip_code').value = '';
  }

  var data = prepareData();

  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  data.page = page;
  data.totalpages = totalpages;
  data.direction = null;

  data.bounds = map.getBounds();
  data.mapbuttonstate = true;

  var request = JSON.stringify(data);

  var query_string = buildQueryString(data);

  $.ajax({
    url: js_app_routing + "/search",
    type: "POST",
    data: request,
    contentType: "application/json; charset=utf-8",
    success: function (info) {
      if (query_string === '') {
        window.history.pushState(null,'hi',document.URL.split("?")[0]);
      } else {
        window.history.pushState(null,'hi',query_string);
      }

      document.getElementById('page').innerHTML = info.page;
      document.getElementById('totalpages').innerHTML = info.totalpages;
      $('#table-wrapper').data('page', info.page);
      $('#table-wrapper').data('totalpages', info.totalpages);
      $('#table-wrapper').data('pagelength', info.pagelength);
      $("#tbody").html(info.tabletemplate);
      $("#table-footer-wrapper").trigger("updateAll");

      document.getElementById('results_language').innerHTML = info.results_language;
      document.getElementById('results-not-found').style.display = info.show_results;

      //console.log('success data:', data);
      //console.log('data.neighborhood:', data.neighborhood);

      if (typeof data.neighborhood !== 'undefined') {
        console.log('data.neighborhood:', data.neighborhood);
        selectedNeighborhood(data.neighborhood);
      }

      updateMap(info.jsdata, 1);
    }
  });
}

function doSearch(category) {
  var data = prepareData(category);

  //console.log('category:', category);

  var nbhd_text, zip_text;

  if (window.location.search.substring(0).match(/nbhd\=(.*)/i) !== null) {
    nbhd_text = decodeURIComponent(window.location.search.substring(0).match(/nbhd\=(.*)/i)[1]);
    //console.log('nbhd_text:', nbhd_text);
  }

  if (window.location.search.substring(0).match(/zip\=(.*)/i) !== null) {
    zip_text = window.location.search.substring(0).match(/zip\=(.*)/i)[1];
  }

  if (document.getElementById('name_address_box').value.trim() === nbhd_text) {
    data.name_address = '';
    data.neighborhood = nbhd_text;
    // Handle if neighborhood in search bar AND in neighborhood dropdown. favor dropdown
    if (document.getElementById('neighborhood').value !== '') {
      document.getElementById('name_address_box').value = '';
      data.neighborhood = document.getElementById('neighborhood').value;
    }
  }

  if (document.getElementById('name_address_box').value.trim() === zip_text) {
    data.name_address = '';
    data.zip_code = zip_text;
    if (document.getElementById('zip_code').value !== '') {
      document.getElementById('name_address_box').value = '';
      data.zip_code = document.getElementById('zip_code').value;
    }
  }

  var bounds = map.getBounds();
  data.bounds = bounds;

  if (document.getElementById('neighborhood').value !== '' || document.getElementById('zip_code').value !== '' || typeof category !== 'undefined') {
    document.getElementById("mapButton").checked = false;
  }

  var mapbuttonstate = document.getElementById("mapButton").checked;
  data.mapbuttonstate = mapbuttonstate;

  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  data.page = page;
  data.totalpages = totalpages;
  data.direction = null;

  var maprequest = JSON.stringify(data);

  // Build query string. Only include non-empty parameters and let Python do the rest
  var query_string = buildQueryString(data);

  $.ajax({
    url: js_app_routing + "/search",
    type: "POST",
    data: maprequest,
    contentType: "application/json; charset=utf-8",
    success: function (info) {
      //console.log('info:', info);

      if (query_string === '') {
        window.history.pushState(null,'hi',document.URL.split("?")[0]);
      } else {
        window.history.pushState(null,'hi',query_string);
      }
      document.getElementById('page').innerHTML = info.page;
      document.getElementById('totalpages').innerHTML = info.totalpages;

      $('#table-wrapper').data('page', info.page);
      $('#table-wrapper').data('totalpages', info.totalpages);
      $('#table-wrapper').data('pagelength', info.pagelength);

      $("#tbody").html(info.tabletemplate);
      $("#table-footer-wrapper").trigger("updateAll");

      document.getElementById('results_language').innerHTML = info.results_language;
      document.getElementById('results-not-found').style.display = info.show_results;

      //console.log('success data:', data);
      //console.log('data.neighborhood:', data.neighborhood);

      if (typeof data.neighborhood !== 'undefined') {
        console.log('data.neighborhood:', data.neighborhood);
        selectedNeighborhood(data.neighborhood);
      }

      updateMap(info.jsdata, 0);
    }
  });
}

$("body").on("click", ".pageforward", function () {
  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  if (page !== totalpages) {
    var data = prepareData();

    data.bounds = map.getBounds();

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
      url: js_app_routing + "/search",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        document.getElementById('page').innerHTML = info.page;
        document.querySelector('#table-wrapper').dataset.page = info.page;

        document.getElementById('totalpages').innerHTML = info.totalpages;
        document.querySelector('#table-wrapper').dataset.totalpages = info.totalpages;

        $("#tbody").html(info.tabletemplate);
        $("#table-footer-wrapper").trigger("updateAll");
        document.getElementById('results_language').innerHTML = info.results_language;

        //console.log('success data:', data);
        //console.log('data.neighborhood:', data.neighborhood);

        if (typeof data.neighborhood !== 'undefined') {
          console.log('data.neighborhood:', data.neighborhood);
          selectedNeighborhood(data.neighborhood);
        }

        updateMap(info.jsdata, 0, 1);

        // Check if this is the last possible page. If so, disable forward button option.
        //console.log('info.page:', info.page);
        if (info.page === 1) {
          document.getElementById('back_button').style.color = 'gray';
          document.getElementById('back_button').style.cursor = 'default';
        } else {
          document.getElementById('back_button').style.color = '#222';
          document.getElementById('back_button').style.cursor = 'pointer';
        }

        if (info.page === info.totalpages) {
          document.getElementById('forward_button').style.color = 'gray';
          document.getElementById('forward_button').style.cursor = 'default';
        } else {
          document.getElementById('forward_button').style.color = '#222';
          document.getElementById('forward_button').style.cursor = 'pointer';
        }
      }
    });
  }
});

$("body").on("click", ".pageback", function () {
  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  if (page !== "1") {
    var data = prepareData();

    data.bounds = map.getBounds();

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
      url: js_app_routing + "/search",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        document.getElementById('page').innerHTML = info.page;
        document.querySelector('#table-wrapper').dataset.page = info.page;

        document.getElementById('totalpages').innerHTML = info.totalpages;
        document.querySelector('#table-wrapper').dataset.totalpages = info.totalpages;

        $("#tbody").html(info.tabletemplate);
        $("#table-footer-wrapper").trigger("updateAll");

        document.getElementById('results_language').innerHTML = info.results_language;

        //console.log('success data:', data);
        //console.log('data.neighborhood:', data.neighborhood);

        if (typeof data.neighborhood !== 'undefined') {
          console.log('data.neighborhood:', data.neighborhood);
          selectedNeighborhood(data.neighborhood);
        }

        updateMap(info.jsdata, 0, 1);

        // Check if this is the last possible page. If so, disable forward button option.
        //console.log('info.page:', info.page);
        //console.log('info.page:', typeof info.page);
        if (info.page === 1) {
          document.getElementById('back_button').style.color = 'gray';
          document.getElementById('back_button').style.cursor = 'default';
        } else {
          document.getElementById('back_button').style.color = '#222';
          document.getElementById('back_button').style.cursor = 'pointer';
        }

        if (info.page === info.totalpages) {
          document.getElementById('forward_button').style.color = 'gray';
          document.getElementById('forward_button').style.cursor = 'default';
        } else {
          document.getElementById('forward_button').style.color = '#222';
          document.getElementById('forward_button').style.cursor = 'pointer';
        }
      }
    });
  }
});

function doPostBack(data) {
  var searchrequest = JSON.stringify(data);
  var query_string = buildQueryString(data);
  $.ajax({
    url: js_app_routing + "/search",
    type: "POST",
    data: searchrequest,
    contentType: "application/json; charset=utf-8",
    success: function (info) {
      if (query_string === '') {
        window.history.pushState(null,'hi',document.URL.split("?")[0]);
      } else {
        // var testarr = document.URL.split('?')[0].split('');
        // testarr.splice(-1, 1);
        // var root_url = testarr.join('');
        window.history.pushState(null,'hi',query_string);
      }
      $("#map-table-wrapper").html(info.template1);
      $("#map-table-wrapper").trigger("updateAll");
      document.getElementById('map-table-wrapper').style.display = 'block';
      document.getElementById('foot').style.display = 'block';

      initialMapFunction(info.jsdata);
    }
  });
}

function populateSearchParameters(parameters) {
  //console.log('parameters.name_address:', (parameters.name_address).length);
  //console.log('parameters.name_address:', typeof parameters.name_address);
  document.getElementById('name_address_box').value = parameters.name_address;
  document.getElementById('amount1').value = (parameters.amountlow !== '' ? '$' : '') + parameters.amountlow;
  document.getElementById('amount2').value = (parameters.amounthigh !== '' ? '$' : '') + parameters.amounthigh;
  document.getElementById('date1').value = parameters.begindate;
  document.getElementById('date2').value = parameters.enddate;
  if (parameters.name_address === '') {
    if (parameters.neighborhood !== '') {
      document.getElementById('name_address_box').value = parameters.neighborhood;
    } else {
      document.getElementById('name_address_box').value = parameters.zip_code;
    }
  }
  if(parameters.amountlow !== '' || parameters.amounthigh !== '' || parameters.begindate !== '' || parameters.enddate !== '') {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search <i class="fa fa-caret-up"></i></a>';
  }
}

window.onload = function() {
  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');

  //console.log('test');

  if (page === '1') {
    //console.log('test');
    document.getElementById('back_button').style.color = 'gray';
    document.getElementById('back_button').style.cursor = 'default';
  } else {
    document.getElementById('back_button').style.color = '#222';
    document.getElementById('back_button').style.cursor = 'pointer';
  }

  if (page === totalpages) {
    document.getElementById('forward_button').style.color = 'gray';
    document.getElementById('forward_button').style.cursor = 'default';
  } else {
    document.getElementById('forward_button').style.color = '#222';
    document.getElementById('forward_button').style.cursor = 'pointer';
  }
}

String.prototype.trunc = String.prototype.trunc ||
  function(n) {
    return this.length > n ? this.substr(0, n - 1) + ' ...' : this;
  };

/*
 Not using for now.
*/
/*
function getLocation(data) {
  var position;
  var options = {
    enableHighAccuracy: true,
    timeout: 5000,
    maximumAge: 0
  };
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function(position) {
        data.latitude = position.coords.latitude;
        data.longitude = position.coords.longitude;
        geoSearch(data);
      },
      function(err) {
        return null;
      },
      options);
  } else {
    alert("Geolocation is not supported by this browser.");
    return null;
  }
}
*/

/*
function geoSearch(data) {
  var bounds = map.getBounds();
  data.bounds = bounds;
  var mapbuttonstate = document.getElementById("mapButton").checked;
  data.mapbuttonstate = mapbuttonstate;

  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  data.page = page;
  data.totalpages = totalpages;
  data.direction = null;

  var georequest = JSON.stringify(data);
  var query_string = buildQueryString(data);

  $.ajax({
    url: app_routing + "search",
    type: "POST",
    data: georequest,
    contentType: "application/json; charset=utf-8",
    success: function (info) {
      if (query_string === '') {
        window.history.pushState(null,'hi',document.URL.split("?")[0]);
      } else {
        // var testarr = document.URL.split('?')[0].split('');
        // testarr.splice(-1, 1);
        // var root_url = testarr.join('');
        window.history.pushState(null,'hi',query_string);
      }
      document.getElementById('page').innerHTML = info.page;
      document.getElementById('totalpages').innerHTML = info.totalpages;

      $('#table-wrapper').data('page', info.page);
      $('#table-wrapper').data('totalpages', info.totalpages);
      $('#table-wrapper').data('pagelength', info.pagelength);

      $("#tbody").html(info.tabletemplate);
      $("#table-footer-wrapper").trigger("updateAll");
      document.getElementById('results_language').innerHTML = info.results_language;
      document.getElementById('results-not-found').style.display = info.show_results;

      updateMap(info.jsdata, 0);
    }
  });
}
*/

/*
$(document).on("click", '.searchButton', function (e) {
  if (e.target.id === 'geosearch-button') {
    getLocation(data);
    return;
  }
  doSearch();
});
*/
