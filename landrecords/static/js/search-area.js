var dropdownFocus = 0;//0 for not in focus, 1 for dropdown selection in focus

function resetAmounts(amount_low, amount_high) {
  if (amount_low === 'Please enter a valid amount range.') {
    amount_low = '';
    document.getElementById('amount1').value = "";
  }
  if (amount_high === 'Please enter a valid amount range.') {
    amount_high = '';
    document.getElementById('amount2').value = "";
  }
  return {low: amount_low, high: amount_high};
}

function resetDates(begin_date, end_date) {
  if (begin_date === 'Please enter a valid date format.' || begin_date === 'Please enter a valid date range.') {
    begin_date = '';
    document.getElementById('date1').value = "";
  }
  if (end_date === 'Please enter a valid date format.' || end_date === 'Please enter a valid date range.') {
    end_date = '';
    document.getElementById('date2').value = "";
  }
  return {begin: begin_date, end: end_date};
}

function checkAmounts(amount_low, amount_high) {
  if (isValidAmountRange(amount_low, amount_high) === false) {
    document.getElementById('amount1').value = "Please enter a valid amount range.";
    document.getElementById('amount2').value = "Please enter a valid amount range.";
    return false;
  }
}

function checkDates(begin_date, end_date) {
  var tf;
  if (isValidDate(begin_date) === false) {
    document.getElementById('date1').value = "Please enter a valid date format.";
    tf = false;
  }
  if (isValidDate(end_date) === false) {
    document.getElementById('date2').value = "Please enter a valid date format.";
    tf = false;
  }
  if (isValidDateRange(begin_date, end_date) === false) {
    document.getElementById('date1').value = "Please enter a valid date range.";
    document.getElementById('date2').value = "Please enter a valid date range.";
    tf = false;
  }
  return tf;
}

function buildQueryString(data) {
  var map_query_string = '?';

  if (data.name_address !== '') {
    map_query_string = map_query_string + "q=" + data.name_address;
  }

  if (data.amount_low !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "a1=" + data.amount_low;
  }

  if (data.amount_high !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "a2=" + data.amount_high;
  }

  if (data.begin_date !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "d1=" + data.begin_date;
  }

  if (data.end_date !== '') {
    if (map_query_string !== '?') {
      map_query_string = map_query_string + '&';
    }
    map_query_string = map_query_string + "d2=" + data.end_date;
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
    map_query_string = "";// "?q=&a1=&a2=&d1=&d2=";
  }

  return map_query_string;
}

function prepareData(category) {
  var name_address = encodeURIComponent($('#name-address-box').val());
  var amount_low1 = $('#amount1').val();
  var amount_high1 = $('#amount2').val();
  var amount_low = amount_low1.replace(/[,$]/g, '');
  var amount_high = amount_high1.replace(/[,$]/g, '');
  var begin_date = $('#date1').val();
  var end_date = $('#date2').val();
  var neighborhood = encodeURIComponent($('#neighborhood').val());
  var zip_code = $('#zip-code').val();

  if (typeof category !== 'undefined') {
    if (category === 'neighborhood') {
      neighborhood = encodeURIComponent($('#name-address-box').val());
      name_address = '';
    }

    if (category === 'zip_code') {
      zip_code = encodeURIComponent($('#name-address-box').val());
      name_address = '';
    }
  }

  var data = {};

  var amounts = resetAmounts(amount_low, amount_high);
  amount_low = amounts['low'];
  amount_high = amounts['high'];

  if (checkAmounts(amount_low, amount_high) === false) {
    data = false;
    return data;
  }

  var dates = resetDates(begin_date, end_date);
  begin_date = dates['begin'];
  end_date = dates['end'];

  if (checkDates(begin_date, end_date) === false) {
    data = false;
    return data;
  }

  data.name_address = name_address;
  data.amount_low = amount_low;
  data.amount_high = amount_high;
  data.begin_date = begin_date;
  data.end_date = end_date;
  data.neighborhood = neighborhood;
  data.zip_code = zip_code;
  data.page_length = 10;

  return data;
}

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

function formatCurrency(number) {
  var n = number.split('').reverse().join("");
  var n2 = n.replace(/\d\d\d(?!$)/g, "$&,");
  var return_val = '$' + n2.split('').reverse().join('');
  return return_val;
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
    if (dropdownFocus === 0) {
      doSearch();
    } else {
      dropdownFocus = 0;
    }
  }
});

//if (isIE || isFirefox || isSafari && !(/iPhone|iPad|iPod/i.test(navigator.userAgent)) ) {
$( "#date1" ).datepicker({
    minDate: new Date(2014, 1, 18)
  });
$( "#date2" ).datepicker();

if ($(window).width() < 500) {
  $('#name-address-box').attr('placeholder','Enter buyer, seller, address');
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

function isValidDateRange(begin_date, end_date) {
  var parts1 = begin_date.split("/");
  var day1 = parseInt(parts1[1], 10);
  var month1 = parseInt(parts1[0], 10);
  var year1 = parseInt(parts1[2], 10);

  var parts2 = end_date.split("/");
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
 * jQuery Autocomplete
 */
$('#name-address-box').catcomplete({//autocomplete({
  source: function (request, response) {
    $.ajax({
      url: js_app_routing + "/input" + "?q=" + request.term,
      contentType: "application/json; charset=utf-8",
      success: function (info) {
        response(info.response);
      }
    });
  },
  select: function(event, ui) {
    dropdownFocus = 1;
    var thisCategory = ui.item.category;
    var thisValue = ui.item.value;

    if (thisCategory === 'Neighborhoods') {
      document.getElementById('name-address-box').value = thisValue;
      document.activeElement.blur();
      doSearch('neighborhood');
      return false;
    } else if (thisCategory === 'ZIP codes') {
      document.getElementById('name-address-box').value = thisValue;
      document.activeElement.blur();
      doSearch('zip_code');
      return false;
    } else {
      document.getElementById('name-address-box').value = thisValue;
      document.activeElement.blur();
      doSearch();
    }
  },
  minLength: 1,
  delay: 0,
  search: function() {
    $('#name-address-box').catcomplete("close");
    //Don't try blur here. It caused problems with down arrow. leave commented
  },
  open: function(event, ui) {
    var input_width = $('#input-div').width();//todo: 
    $('.ui-menu').width(input_width);
  }
}).keyup(function (event) {
  if (event.which === 13) {
    $('#name-address-box').catcomplete("close");
    document.activeElement.blur();
  }
});

/* 
 * Search button clicked
 */
$(document).on("click", '.searchButton', function () {
  doSearch();
});

/*
 * Check if GCS completed or not showing
 */
function checkForChanges() {
  var gcsTimeout;
  if ($('button.t402-elided').length) {
    // console.log('gcs not cleared');
    //console.log($('button.t402-elided'));
    gcsTimeout = setTimeout(checkForChanges, 500);
  } else {
    // console.log('gcs cleared');
    clearTimeout(gcsTimeout);
    $('.p402_premium').css({'display': 'none'});
    $('button').addClass('searchButton');
  }
}

checkForChanges();
