/*
 * If amount previously had an error, replace error message to allow for another search.
 */
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

/*
 * If date previously had an error, replace error message to allow for another search.
 */
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

/*
 * Run checks on amounts.
 */
function checkAmounts(amountlow, amounthigh) {
  if (isValidAmountRange(amountlow, amounthigh) === false) {
    //$("body").removeClass("loading");
    console.log('false');
    document.getElementById('amount1').value = "Please enter a valid amount range.";
    document.getElementById('amount2').value = "Please enter a valid amount range.";
    return false;
  }
}

/*
 * Run checks on dates.
 */
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

/*
 * Hide/show advanced search options.
 */
$("#advanced-search").on("click", function () {
  if ($('#filters').css('display') === 'none') {
    document.getElementById('filters').style.display = 'block';
    document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search <i class="fa fa-caret-up"></i></a>';
  }
  else {
    document.getElementById('filters').style.display = 'none';
    document.getElementById('advanced-search').innerHTML = '<a>Show advanced search <i class="fa fa-caret-down"></i></a>';
  }
});

$("#search-note").on("click", function () {
  document.getElementById('filters').style.display = 'block';
  document.getElementById('advanced-search').innerHTML = '<a>Hide advanced search <i class="fa fa-caret-up"></i></a>';
});

/*
 * Format amounts with $ and commas.
 */
function formatCurrency(number) {
  var n = number.split('').reverse().join("");
  var n2 = n.replace(/\d\d\d(?!$)/g, "$&,");
  return '$' + n2.split('').reverse().join('');
}

/*
 * Format currency as the user types the input
 */
$('.currency').on('input', function () {
  $(this).val(formatCurrency(this.value.replace(/[,$]/g, '')));
}).on('keypress', function (e) {
  if (!$.isNumeric(String.fromCharCode(e.which)) && (e.which !== 8)) {
    e.preventDefault();
  }
});

/*
 * User jQuery's datepicker library for the date inputs.
 */
$( "#date1" ).datepicker({
    minDate: new Date(2014, 1, 18)
  });
$( "#date2" ).datepicker();

/*
 * Change placeholder text for smaller screens.
 */
if ($(window).width() < 500) {
  $('#name_address_box').attr('placeholder','Enter buyer, seller, address, zip');
  $('#date1').attr('placeholder','');
  $('#date2').attr('placeholder','');
}

/*
 * Check that date is formatted correctly.
 */
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

/*
 * Check that date bounds are logical
 */
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

/*
 * Check that amount bounds are logical
 */
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

/*
 * jQuery Autocomplete
 */
$.widget( "custom.catcomplete", $.ui.autocomplete, {
  _create: function() {
    this._super();
    this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
  },
  _renderMenu: function( ul, items ) {
    var that = this,
      currentCategory = "";
    $.each( items, function( index, item ) {
      var li;
      if ( item.category != currentCategory ) {
        ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
        currentCategory = item.category;
      }
      li = that._renderItemData( ul, item );
      if ( item.category ) {
        li.attr( "aria-label", item.category + " : " + item.label );
      }
    });
  },
});

/*
 * Format input autocomplete according to the categories (location, buyer, seller)
 */
$('#name_address_box').catcomplete({//autocomplete({
  source: function (request, response) {
    $.ajax({
      url: "/realestate/input" + "?q=" + request.term,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        //console.log('info: ', info.response);
        response(info.response);
      }
    });
  },
  select: function(event, ui) {
    $('#name_address_box').val(ui.item.value);
    $('.searchButton').click();
  },
  minLength: 2,
  delay: 0,
  open: function() {
    var input_width = $('#input-div').width();
    $('.ui-menu').width(input_width);
  }
}).keyup(function (event) {//Hitting enter to search will also close close autocomplete dropdown menu
  if (event.which === 13) {
    $('#name_address_box').catcomplete("close");
  }
});

/*
 * Use input parameters to format search URL
 */
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

  if (data.neighborhood !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "nbhd=" + data.neighborhood;
  }

  if (data.zip_code !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "zip=" + data.zip_code;
  }

  if (map_query_string == '?') {
    map_query_string = "?q=&a1=&a2=&d1=&d2=";
  }

  console.log('map_query_string: ', map_query_string);

  return map_query_string;
}

/*
 * GET call for /realestate/search
 */
function getSearchPage(data) {
  console.log('getSearchPage');
  console.log('data: ', data);
  var query_string = buildQueryString(data);
  console.log('query_string: ', query_string);
  console.log('typeof query_string: ', typeof query_string);
  query_string = "/realestate/search" + query_string;
  //$.get(query_string);
  window.location.href = query_string;
}

/*
 * Gather search input and prepare for GET call to /realestate/search
 */
function prepareGET() {
  var name_address = encodeURIComponent($('#name_address_box').val());
  var amountlow1 = $('#amount1').val();
  var amounthigh1 = $('#amount2').val();
  var amountlow = amountlow1.replace(/[,$]/g, '');
  var amounthigh = amounthigh1.replace(/[,$]/g, '');
  var begindate = $('#date1').val();
  var enddate = $('#date2').val();
  var neighborhood = encodeURIComponent($('#neighborhood-dropdown').val());
  var zip_code = $('#zip-dropdown').val();

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

  data.neighborhood = neighborhood;
  data.zip_code = zip_code;

  return data;
}

/* 
 * Search button clicked
 */
$(document).on("click", '.searchButton', function () {
  var data = prepareGET();
  // if (data === false) {//todo: what is this for?
  //   return;
  // }
  getSearchPage(data);
});

$(document.body).keyup(function (event) {
  if (event.which === 13) {
    $(".searchButton").click();
  }
});

/*
 * Check if GCS completed or not showing
 */
function checkForChanges() {
  console.log('gcs');
  var gcsTimeout;
  if ($('button.t402-elided').length) {
    gcsTimeout = setTimeout(checkForChanges, 500);
  } else {
    clearTimeout(gcsTimeout);
    $('button').addClass('searchButton');
  }
}

document.onload = checkForChanges();// Check on GCS
