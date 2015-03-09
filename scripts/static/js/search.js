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
  /*
   Map movement filter is turned on.
  */

  var nbhd_text, zip_text;

  if (window.location.search.substring(0).match(/nbhd\=(.*)/i) !== null) {
    nbhd_text = decodeURIComponent(window.location.search.substring(0).match(/nbhd\=(.*)/i)[1]);
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

      var table_wrapper = document.querySelector('#table-wrapper');
      table_wrapper.setAttribute('data-page', info.page);
      table_wrapper.setAttribute('data-totalpages', info.totalpages);
      table_wrapper.setAttribute('data-pagelength', info.pagelength);

      $("#tbody").html(info.tabletemplate);
      $("#table-footer-wrapper").trigger("updateAll");

      document.getElementById('results_language').innerHTML = info.results_language;
      document.getElementById('results-not-found').style.display = info.show_results;

      //console.log('data.neighborhood:', data.neighborhood);

      if (typeof data.neighborhood !== 'undefined' && data.neighborhood !== '') {
        selectedNeighborhood(data.neighborhood);
        updateMap(info.jsdata, 1, 0, 1);
      } else {
        removeNeighborhoodLayer();
        updateMap(info.jsdata, 1, 0, 0);
      }

      checkPagerButtons(info.page, info.totalpages)
    }
  });
}

function doSearch(category) {
  var data = prepareData(category);
  var nbhd_text, zip_text;

  // Get URL's neighborhood value
  if (window.location.search.substring(0).match(/nbhd\=(.*)/i) !== null) {
    nbhd_text = decodeURIComponent(window.location.search.substring(0).match(/nbhd\=(.*)/i)[1]);
  }

  // Get URL's zip value
  if (window.location.search.substring(0).match(/zip\=(.*)/i) !== null) {
    zip_text = window.location.search.substring(0).match(/zip\=(.*)/i)[1];
  }

  // If search input is still equal to the neighborhood previously searched for, keep in search bar and continue to use as neighborhood, not as keyword.
  if (document.getElementById('name_address_box').value.trim() === nbhd_text) {
    data.name_address = '';
    data.neighborhood = nbhd_text;

    // Handle if neighborhood in search bar AND is now also in neighborhood dropdown. favor dropdown
    if (document.getElementById('neighborhood').value !== '') {
      document.getElementById('name_address_box').value = ''; // Overwriting this will affect checks below
      data.neighborhood = document.getElementById('neighborhood').value;
    }
  }

  // If search input is still equal to the zip code previously searched for, keep in search bar and continue to use as zip, not as keyword.
  if (document.getElementById('name_address_box').value.trim() === zip_text) {
    data.name_address = '';
    data.zip_code = zip_text;

    if (document.getElementById('zip_code').value !== '') {
      document.getElementById('name_address_box').value = '';
      data.zip_code = document.getElementById('zip_code').value;
    }
  }



  // If neighborhood dropdown selection is equal to the neighborhood previously searched for (in the URL), but there is now a neighborhood in the search input, remove the neighborhood dropdown and favor the search input.
  if (document.getElementById('neighborhood').value === nbhd_text && category === 'neighborhood') {
    document.getElementById('neighborhood').value = '';
    data.neighborhood = document.getElementById('name_address_box').value;
    data.name_address = '';
  }

  // If zip dropdown selection is equal to the zip previously searched for (in the URL), but there is now a zip in the search input, remove the zip dropdown and favor the search input.
  if (document.getElementById('zip_code').value === zip_text && category === 'zip_code') {
    document.getElementById('zip_code').value = '';
    data.zip_code = document.getElementById('name_address_box').value;
    data.name_address = '';
  }





  // Disable map-view filtering if new searches uses geographic parameters
  if (document.getElementById('neighborhood').value !== '' || document.getElementById('zip_code').value !== '' || typeof category !== 'undefined') {
    document.getElementById("mapButton").checked = false;
  }

  data.bounds = map.getBounds();
  data.mapbuttonstate = document.getElementById("mapButton").checked;
  data.page = $('#table-wrapper').attr('data-page');
  data.totalpages = $('#table-wrapper').attr('data-totalpages');
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
      if (query_string === '') {
        window.history.pushState(null,'hi',document.URL.split("?")[0]);
      } else {
        window.history.pushState(null,'hi',query_string);
      }
      
      document.getElementById('page').innerHTML = info.page;
      document.getElementById('totalpages').innerHTML = info.totalpages;

      var table_wrapper = document.querySelector('#table-wrapper');
      table_wrapper.setAttribute('data-page', info.page);
      table_wrapper.setAttribute('data-totalpages', info.totalpages);
      table_wrapper.setAttribute('data-pagelength', info.pagelength);

      $("#tbody").html(info.tabletemplate);
      $("#table-footer-wrapper").trigger("updateAll");

      document.getElementById('results_language').innerHTML = info.results_language;
      document.getElementById('results-not-found').style.display = info.show_results;

      //console.log('data.neighborhood:', data.neighborhood);

      if (typeof data.neighborhood !== 'undefined' && data.neighborhood !== '') {
        selectedNeighborhood(data.neighborhood);
        updateMap(info.jsdata, 0, 0, 1);
      } else {
        removeNeighborhoodLayer();
        updateMap(info.jsdata, 0, 0, 0);
      }

      checkPagerButtons(info.page, info.totalpages)
    }
  });
}

$("body").on("click", ".pageforward", function () {
  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  
  //console.log('\npage:',  page);
  //console.log('totalpages:', totalpages);

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
        document.getElementById('totalpages').innerHTML = info.totalpages;

        var table_wrapper = document.querySelector('#table-wrapper');
        table_wrapper.setAttribute('data-page', info.page);
        table_wrapper.setAttribute('data-totalpages', info.totalpages);
        table_wrapper.setAttribute('data-pagelength', info.pagelength);

        $("#tbody").html(info.tabletemplate);
        $("#table-footer-wrapper").trigger("updateAll");
        document.getElementById('results_language').innerHTML = info.results_language;

        //console.log('data.neighborhood:', data.neighborhood);

        if (typeof data.neighborhood !== 'undefined' && data.neighborhood !== '') {
          selectedNeighborhood(data.neighborhood);
          updateMap(info.jsdata, 0, 1, 1);
        } else {
          removeNeighborhoodLayer();
          updateMap(info.jsdata, 0, 1, 0);
        }

        checkPagerButtons(info.page, info.totalpages)

        //console.log('info.page:', info.page);
        //console.log('info.totalpages:', info.totalpages);
      }
    });
  }
});

$("body").on("click", ".pageback", function () {
  var page = $('#table-wrapper').attr('data-page');
  var totalpages = $('#table-wrapper').attr('data-totalpages');
  if (page !== "1" && page !== "0") {
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
        document.getElementById('totalpages').innerHTML = info.totalpages;

        var table_wrapper = document.querySelector('#table-wrapper');
        table_wrapper.setAttribute('data-page', info.page);
        table_wrapper.setAttribute('data-totalpages', info.totalpages);
        table_wrapper.setAttribute('data-pagelength', info.pagelength);

        $("#tbody").html(info.tabletemplate);
        $("#table-footer-wrapper").trigger("updateAll");

        document.getElementById('results_language').innerHTML = info.results_language;

        ////console.log('data.neighborhood:', data.neighborhood);

        if (typeof data.neighborhood !== 'undefined' && data.neighborhood !== '') {
          selectedNeighborhood(data.neighborhood);
          updateMap(info.jsdata, 0, 1, 1);
        } else {
          removeNeighborhoodLayer();
          updateMap(info.jsdata, 0, 1, 0);
        }

        checkPagerButtons(info.page, info.totalpages);
      }
    });
  }
});

function populateSearchParameters(parameters) {
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

function checkPagerButtons(page, totalpages) {
  //console.log('yo:');

  if (typeof page === 'undefined') {
    page = $('#table-wrapper').attr('data-page');
  }

  if (typeof totalpages === 'undefined') {
    totalpages = $('#table-wrapper').attr('data-totalpages');
  }

  page = page.toString();
  totalpages = totalpages.toString();

  ////console.log('page:', page);
  ////console.log('totalpages:', totalpages);

  if (page === '1' || page === '0') {
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

checkPagerButtons();


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
