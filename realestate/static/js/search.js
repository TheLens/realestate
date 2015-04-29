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
  if (document.getElementById('name-address-box').value.trim() === nbhd_text || document.getElementById('name-address-box').value.trim() === zip_text) {
    document.getElementById('name-address-box').value = '';
  }

  if (document.getElementById('neighborhood').value !== '') {
    document.getElementById('neighborhood').value = '';
  }

  if (document.getElementById('zip-code').value !== '') {
    document.getElementById('zip-code').value = '';
  }

  var data = prepareData();

  var current_page = $('#table-wrapper').attr('data-current-page');
  current_page = parseInt(current_page, 10);
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  number_of_pages = parseInt(number_of_pages, 10);
  data.current_page = current_page;
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

      document.getElementById('current-page').innerHTML = info.data.current_page;
      document.getElementById('number-of-pages').innerHTML = info.data.number_of_pages;

      var table_wrapper = document.querySelector('#table-wrapper');
      table_wrapper.setAttribute('data-current-page', info.data.current_page);
      table_wrapper.setAttribute('data-number-of-pages', info.data.number_of_pages);
      table_wrapper.setAttribute('data-page-length', info.data.page_length);

      $("#tbody").html(info.table_template);
      $("#table-footer-wrapper").trigger("updateAll");

      document.getElementById('results-language').innerHTML = info.data.results_language;
      document.getElementById('results-not-found').style.display = info.data.show_results;

      if (typeof info.data.neighborhood !== 'undefined' && info.data.neighborhood !== '') {
        selectedNeighborhood(info.data.neighborhood);
        updateMap(info.js_data, 1, 0, 1);
      } else {
        removeNeighborhoodLayer();
        updateMap(info.js_data, 1, 0, 0);
      }

      checkPagerButtons(info.data.current_page, info.data.number_of_pages);
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
  if (document.getElementById('name-address-box').value.trim() === nbhd_text) {
    data.name_address = '';
    data.neighborhood = nbhd_text;

    // Handle if neighborhood in search bar AND is now also in neighborhood dropdown. favor dropdown
    if (document.getElementById('neighborhood').value !== '') {
      document.getElementById('name-address-box').value = ''; // Overwriting this will affect checks below
      data.neighborhood = document.getElementById('neighborhood').value;
    }
  }

  // If search input is still equal to the zip code previously searched for, keep in search bar and continue to use as zip, not as keyword.
  if (document.getElementById('name-address-box').value.trim() === zip_text) {
    data.name_address = '';
    data.zip_code = zip_text;

    if (document.getElementById('zip-code').value !== '') {
      document.getElementById('name-address-box').value = '';
      data.zip_code = document.getElementById('zip-code').value;
    }
  }

  // If neighborhood dropdown selection is equal to the neighborhood previously searched for (in the URL), but there is now a neighborhood in the search input, remove the neighborhood dropdown and favor the search input.
  if (document.getElementById('neighborhood').value === nbhd_text && category === 'neighborhood') {
    document.getElementById('neighborhood').value = '';
    data.neighborhood = document.getElementById('name-address-box').value;
    data.name_address = '';
  }

  // If zip dropdown selection is equal to the zip previously searched for (in the URL), but there is now a zip in the search input, remove the zip dropdown and favor the search input.
  if (document.getElementById('zip-code').value === zip_text && category === 'zip_code') {
    document.getElementById('zip-code').value = '';
    data.zip_code = document.getElementById('name-address-box').value;
    data.name_address = '';
  }





  // Disable map-view filtering if new searches uses geographic parameters
  if (document.getElementById('neighborhood').value !== '' || document.getElementById('zip-code').value !== '' || typeof category !== 'undefined') {
    document.getElementById("map-button").checked = false;
  }

  data.bounds = map.getBounds();
  data.map_button_state = document.getElementById("map-button").checked;
  var current_page = $('#table-wrapper').attr('data-current-page');
  current_page = parseInt(current_page, 10);
  data.current_page = current_page;
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  number_of_pages = parseInt(number_of_pages, 10);
  data.number_of_pages = number_of_pages;
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
      
      document.getElementById('current-page').innerHTML = info.data.current_page;
      document.getElementById('number-of-pages').innerHTML = info.data.number_of_pages;

      var table_wrapper = document.querySelector('#table-wrapper');
      table_wrapper.setAttribute('data-current-page', info.data.current_page);
      table_wrapper.setAttribute('data-number-of-pages', info.data.number_of_pages);
      table_wrapper.setAttribute('data-page-length', info.data.page_length);

      $("#tbody").html(info.table_template);
      $("#table-footer-wrapper").trigger("updateAll");

      document.getElementById('results-language').innerHTML = info.data.results_language;
      document.getElementById('results-not-found').style.display = info.data.show_results;

      if (typeof info.data.neighborhood !== 'undefined' && info.data.neighborhood !== '') {
        selectedNeighborhood(info.data.neighborhood);
        updateMap(info.js_data, 0, 0, 1);
      } else {
        removeNeighborhoodLayer();
        updateMap(info.js_data, 0, 0, 0);
      }

      checkPagerButtons(info.data.current_page, info.data.number_of_pages);
    }
  });
}

$("body").on("click", ".page-forward", function () {
  var current_page = $('#table-wrapper').attr('data-current-page');
  current_page = parseInt(current_page, 10);
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  number_of_pages = parseInt(number_of_pages, 10);

  if (current_page !== number_of_pages) {
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
    if (document.getElementById('name-address-box').value.trim() === nbhd_text) {
      data.name_address = '';
      data.neighborhood = nbhd_text;

      // Handle if neighborhood in search bar AND is now also in neighborhood dropdown. favor dropdown
      if (document.getElementById('neighborhood').value !== '') {
        document.getElementById('name-address-box').value = ''; // Overwriting this will affect checks below
        data.neighborhood = document.getElementById('neighborhood').value;
      }
    }

    // If search input is still equal to the zip code previously searched for, keep in search bar and continue to use as zip, not as keyword.
    if (document.getElementById('name-address-box').value.trim() === zip_text) {
      data.name_address = '';
      data.zip_code = zip_text;

      if (document.getElementById('zip-code').value !== '') {
        document.getElementById('name-address-box').value = '';
        data.zip_code = document.getElementById('zip-code').value;
      }
    }

    // If neighborhood dropdown selection is equal to the neighborhood previously searched for (in the URL), but there is now a neighborhood in the search input, remove the neighborhood dropdown and favor the search input.
    if (document.getElementById('neighborhood').value === nbhd_text && category === 'neighborhood') {
      document.getElementById('neighborhood').value = '';
      data.neighborhood = document.getElementById('name-address-box').value;
      data.name_address = '';
    }

    // If zip dropdown selection is equal to the zip previously searched for (in the URL), but there is now a zip in the search input, remove the zip dropdown and favor the search input.
    if (document.getElementById('zip-code').value === zip_text && category === 'zip_code') {
      document.getElementById('zip-code').value = '';
      data.zip_code = document.getElementById('name-address-box').value;
      data.name_address = '';
    }

    data.bounds = map.getBounds();

    var map_button_state = document.getElementById("map-button").checked;
    data.map_button_state = map_button_state;

    //Find pagination details
    var page_length = $('#table-wrapper').attr('data-page-length');
    page_length = parseInt(page_length, 10);
    data.current_page = current_page;
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
        console.log('returned info:', info);
        document.getElementById('current-page').innerHTML = info.data.current_page;
        document.getElementById('number-of-pages').innerHTML = info.data.number_of_pages;

        var table_wrapper = document.querySelector('#table-wrapper');

        //console.log($('#table-wrapper').attr('data-current-page'));
        //console.log('current_page:', info.data.current_page);
        //console.log('typeof current_page:', typeof info.data.current_page);
        table_wrapper.setAttribute('data-current-page', info.data.current_page);
        //console.log($('#table-wrapper').attr('data-current-page'));

        table_wrapper.setAttribute('data-number-of-pages', info.data.number_of_pages);
        table_wrapper.setAttribute('data-page-length', info.data.page_length);

        //console.log('tbody before:', $("#tbody").html());
        //console.log(info.table_template);
        $("#tbody").html(info.table_template);
        $("#table-footer-wrapper").trigger("updateAll");
        //console.log('tbody after:', $("#tbody").html());
        document.getElementById('results-language').innerHTML = info.data.results_language;

        if (typeof info.data.neighborhood !== 'undefined' && info.data.neighborhood !== '') {
          selectedNeighborhood(info.data.neighborhood);
          updateMap(info.js_data, 0, 1, 1);
        } else {
          removeNeighborhoodLayer();
          updateMap(info.js_data, 0, 1, 0);
        }

        checkPagerButtons(info.data.current_page, info.data.number_of_pages);
      }
    });
  }
});

$("body").on("click", ".page-back", function () {
  var current_page = $('#table-wrapper').attr('data-current-page');
  var number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  if (current_page !== "1" && current_page !== "0") {
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
    if (document.getElementById('name-address-box').value.trim() === nbhd_text) {
      data.name_address = '';
      data.neighborhood = nbhd_text;

      // Handle if neighborhood in search bar AND is now also in neighborhood dropdown. favor dropdown
      if (document.getElementById('neighborhood').value !== '') {
        document.getElementById('name-address-box').value = ''; // Overwriting this will affect checks below
        data.neighborhood = document.getElementById('neighborhood').value;
      }
    }

    // If search input is still equal to the zip code previously searched for, keep in search bar and continue to use as zip, not as keyword.
    if (document.getElementById('name-address-box').value.trim() === zip_text) {
      data.name_address = '';
      data.zip_code = zip_text;

      if (document.getElementById('zip-code').value !== '') {
        document.getElementById('name-address-box').value = '';
        data.zip_code = document.getElementById('zip-code').value;
      }
    }

    // If neighborhood dropdown selection is equal to the neighborhood previously searched for (in the URL), but there is now a neighborhood in the search input, remove the neighborhood dropdown and favor the search input.
    if (document.getElementById('neighborhood').value === nbhd_text && category === 'neighborhood') {
      document.getElementById('neighborhood').value = '';
      data.neighborhood = document.getElementById('name-address-box').value;
      data.name_address = '';
    }

    // If zip dropdown selection is equal to the zip previously searched for (in the URL), but there is now a zip in the search input, remove the zip dropdown and favor the search input.
    if (document.getElementById('zip-code').value === zip_text && category === 'zip_code') {
      document.getElementById('zip-code').value = '';
      data.zip_code = document.getElementById('name-address-box').value;
      data.name_address = '';
    }

    data.bounds = map.getBounds();

    var map_button_state = document.getElementById("map-button").checked;
    data.map_button_state = map_button_state;

    //Find pagination details
    current_page = $('#table-wrapper').attr('data-current-page');
    current_page = parseInt(current_page, 10);
    number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
    number_of_pages = parseInt(number_of_pages, 10);
    var page_length = $('#table-wrapper').attr('data-page-length');
    page_length = parseInt(page_length, 10);
    data.current_page = current_page;
    data.number_of_pages = number_of_pages;
    data.page_length = page_length;
    data.direction = 'back';

    var maprequest = JSON.stringify(data);

    console.log(data);

    $.ajax({
      url: js_app_routing + "/search",
      type: "POST",
      data: maprequest,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        document.getElementById('current-page').innerHTML = info.data.current_page;
        document.getElementById('number-of-pages').innerHTML = info.data.number_of_pages;

        var table_wrapper = document.querySelector('#table-wrapper');
        table_wrapper.setAttribute('data-current-page', info.data.current_page);
        table_wrapper.setAttribute('data-number-of-pages', info.data.number_of_pages);
        table_wrapper.setAttribute('data-page-length', info.data.page_length);

        $("#tbody").html(info.table_template);
        $("#table-footer-wrapper").trigger("updateAll");

        document.getElementById('results-language').innerHTML = info.data.results_language;

        if (typeof info.data.neighborhood !== 'undefined' && info.data.neighborhood !== '') {
          selectedNeighborhood(info.data.neighborhood);
          updateMap(info.js_data, 0, 1, 1);
        } else {
          removeNeighborhoodLayer();
          updateMap(info.js_data, 0, 1, 0);
        }

        checkPagerButtons(info.data.current_page, info.data.number_of_pages);
      }
    });
  }
});

function populateSearchParameters(data) {
  document.getElementById('name-address-box').value = data.name_address;
  document.getElementById('amount1').value = (data.amount_low !== '' ? '$' : '') + data.amount_low;
  document.getElementById('amount2').value = (data.amount_high !== '' ? '$' : '') + data.amount_high;
  document.getElementById('date1').value = data.begin_date;
  document.getElementById('date2').value = data.end_date;
  if (data.name_address === '') {
    if (data.neighborhood !== '') {
      document.getElementById('name-address-box').value = data.neighborhood;
    } else {
      document.getElementById('name-address-box').value = data.zip_code;
    }
  }
  if(data.amount_low !== '' || data.amount_high !== '' || data.begin_date !== '' || data.end_date !== '') {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search <i class="fa fa-caret-up"></i></a>';
  }
}

function checkPagerButtons(current_page, number_of_pages) {
  if (typeof current_page === 'undefined') {
    current_page = $('#table-wrapper').attr('data-current-page');
  }

  if (typeof number_of_pages === 'undefined') {
    number_of_pages = $('#table-wrapper').attr('data-number-of-pages');
  }

  current_page = current_page.toString();
  number_of_pages = number_of_pages.toString();

  if (current_page === '1' || current_page === '0') {
    document.getElementById('back-button').style.color = 'gray';
    document.getElementById('back-button').style.cursor = 'default';
  } else {
    document.getElementById('back-button').style.color = '#222';
    document.getElementById('back-button').style.cursor = 'pointer';
  }

  if (current_page === number_of_pages) {
    document.getElementById('forward-button').style.color = 'gray';
    document.getElementById('forward-button').style.cursor = 'default';
  } else {
    document.getElementById('forward-button').style.color = '#222';
    document.getElementById('forward-button').style.cursor = 'pointer';
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
  var map_button_state = document.getElementById("map-button").checked;
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
      document.getElementById('current-page').innerHTML = info.page;
      document.getElementById('number_of_pages').innerHTML = info.number_of_pages;

      $('#table-wrapper').data('current-page', info.page);
      $('#table-wrapper').data('number_of_pages', info.number_of_pages);
      $('#table-wrapper').data('page_length', info.page_length);

      $("#tbody").html(info.table_template);
      $("#table-footer-wrapper").trigger("updateAll");
      document.getElementById('results_language').innerHTML = info.results_language;
      document.getElementById('results-not-found').style.display = info.show_results;

      updateMap(info.js_data, 0);
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
