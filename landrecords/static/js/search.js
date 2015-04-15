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
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  data.page = page;
  data.number_of_pages = number_of_pages;
  data.direction = null;

  data.bounds = map.getBounds();
  data.map_button_state = true;

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
      document.getElementById('number_of_pages').innerHTML = info.number_of_pages;

      var table_wrapper = document.querySelector('#table-wrapper');
      table_wrapper.setAttribute('data-page', info.page);
      table_wrapper.setAttribute('data-number-of-pages', info.number_of_pages);
      table_wrapper.setAttribute('data-page-length', info.page_length);

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

      checkPagerButtons(info.page, info.number_of_pages);
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
  data.map_button_state = document.getElementById("mapButton").checked;
  data.page = $('#table-wrapper').attr('data-page');
  data.number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
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
      document.getElementById('number_of_pages').innerHTML = info.number_of_pages;

      var table_wrapper = document.querySelector('#table-wrapper');
      table_wrapper.setAttribute('data-page', info.page);
      table_wrapper.setAttribute('data-number-of-pages', info.number_of_pages);
      table_wrapper.setAttribute('data-page-length', info.page_length);

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

      checkPagerButtons(info.page, info.number_of_pages);
    }
  });
}

$("body").on("click", ".pageforward", function () {
  var page = $('#table-wrapper').attr('data-page');
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  
  //console.log('\npage:',  page);
  //console.log('number_of_pages:', number_of_pages);

  if (page !== number_of_pages) {
    var data = prepareData();

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

    data.bounds = map.getBounds();

    var map_button_state = document.getElementById("mapButton").checked;
    data.map_button_state = map_button_state;

    //Find pagination details
    var page_length = $('#table-wrapper').attr('data-page-length');
    data.page = page;
    data.number_of_pages = number_of_pages;
    data.page_length = page_length;
    data.direction = 'forward';

    var maprequest = JSON.stringify(data);
    $.ajax({
      url: js_app_routing + "/search",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        document.getElementById('page').innerHTML = info.page;
        document.getElementById('number_of_pages').innerHTML = info.number_of_pages;

        var table_wrapper = document.querySelector('#table-wrapper');
        table_wrapper.setAttribute('data-page', info.page);
        table_wrapper.setAttribute('data-number-of-pages', info.number_of_pages);
        table_wrapper.setAttribute('data-page-length', info.page_length);

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

        checkPagerButtons(info.page, info.number_of_pages);

        //console.log('info.page:', info.page);
        //console.log('info.number_of_pages:', info.number_of_pages);
      }
    });
  }
});

$("body").on("click", ".pageback", function () {
  var page = $('#table-wrapper').attr('data-page');
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  if (page !== "1" && page !== "0") {
    var data = prepareData();

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

    data.bounds = map.getBounds();

    var map_button_state = document.getElementById("mapButton").checked;
    data.map_button_state = map_button_state;

    //Find pagination details
    page = $('#table-wrapper').attr('data-page');
    number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
    var page_length = $('#table-wrapper').attr('data-page-length');
    data.page = page;
    data.number_of_pages = number_of_pages;
    data.page_length = page_length;
    data.direction = 'back';

    var maprequest = JSON.stringify(data);

    $.ajax({
      url: js_app_routing + "/search",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        document.getElementById('page').innerHTML = info.page;
        document.getElementById('number_of_pages').innerHTML = info.number_of_pages;

        var table_wrapper = document.querySelector('#table-wrapper');
        table_wrapper.setAttribute('data-page', info.page);
        table_wrapper.setAttribute('data-number-of-pages', info.number_of_pages);
        table_wrapper.setAttribute('data-page-length', info.page_length);

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

        checkPagerButtons(info.page, info.number_of_pages);
      }
    });
  }
});

function populateSearchParameters(data) {
  document.getElementById('name_address_box').value = data.name_address;
  document.getElementById('amount1').value = (data.amountlow !== '' ? '$' : '') + data.amountlow;
  document.getElementById('amount2').value = (data.amounthigh !== '' ? '$' : '') + data.amounthigh;
  document.getElementById('date1').value = data.begindate;
  document.getElementById('date2').value = data.enddate;
  if (data.name_address === '') {
    if (data.neighborhood !== '') {
      document.getElementById('name_address_box').value = data.neighborhood;
    } else {
      document.getElementById('name_address_box').value = data.zip_code;
    }
  }
  if(data.amountlow !== '' || data.amounthigh !== '' || data.begindate !== '' || data.enddate !== '') {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search <i class="fa fa-caret-up"></i></a>';
  }
}

function checkPagerButtons(page, number_of_pages) {
  //console.log('yo:');

  if (typeof page === 'undefined') {
    page = $('#table-wrapper').attr('data-page');
  }

  if (typeof number_of_pages === 'undefined') {
    number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  }

  page = page.toString();
  number_of_pages = number_of_pages.toString();

  ////console.log('page:', page);
  ////console.log('number_of_pages:', number_of_pages);

  if (page === '1' || page === '0') {
    document.getElementById('back_button').style.color = 'gray';
    document.getElementById('back_button').style.cursor = 'default';
  } else {
    document.getElementById('back_button').style.color = '#222';
    document.getElementById('back_button').style.cursor = 'pointer';
  }

  if (page === number_of_pages) {
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
  var map_button_state = document.getElementById("mapButton").checked;
  data.map_button_state = map_button_state;

  var page = $('#table-wrapper').attr('data-page');
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  data.page = page;f
  data.number_of_pages = number_of_pages;
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
      document.getElementById('number_of_pages').innerHTML = info.number_of_pages;

      $('#table-wrapper').data('page', info.page);
      $('#table-wrapper').data('number_of_pages', info.number_of_pages);
      $('#table-wrapper').data('page_length', info.page_length);

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
