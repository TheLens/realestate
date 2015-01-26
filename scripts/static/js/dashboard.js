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

  var instrument_no = $('#instrument_no_' + loop_index).text();
  console.log('instrument_no:', instrument_no);

  var detail_publish = $('#detail_publish_' + loop_index).text();
  var location_publish = $('#location_publish_' + loop_index).text();

  var document_date = $('#document_date_' + loop_index).text();
  var amount = $('#amount_' + loop_index).text();
  var location = $('#location_' + loop_index).text();
  var sellers = $('#sellers_' + loop_index).text();
  var buyers = $('#buyers_' + loop_index).text();
  var document_recorded = $('#document_recorded_' + loop_index).text();
  var latitude = $('#latitude_' + loop_index).text();
  var longitude = $('#longitude_' + loop_index).text();
  var zip_code = $('#zip_code_' + loop_index).text();
  var neighborhood = $('#neighborhood_' + loop_index).text();

  var data = {};

  data.instrument_no = instrument_no;
  data.detail_publish = detail_publish;
  data.location_publish = location_publish;

  data.document_date = document_date;
  data.amount = amount;
  data.location = location;
  data.sellers = sellers;
  data.buyers = buyers;
  data.document_recorded = document_recorded;
  data.latitude = latitude;
  data.longitude = longitude;
  data.zip_code = zip_code;
  data.neighborhood = neighborhood;

  console.log('data:', data);

  return data;
}

function showPreview(data) {
  console.log(data.instrument_no);
  document.getElementById('preview_instrument_no').innerHTML = data.instrument_no;
  document.getElementById('preview').style.display = "block";
}

$(document).on("click", '.searchButton', function (e) {
  console.log('e:', e);
  var loop_index = $(event.target).attr('id');
  console.log('loop_index:', loop_index);

  var data = preparePOST(loop_index);

  //Prompt preview and double-check
  showPreview(data);

  $(document).on("click", '.searchButtonTrue', function () {
    doPostBack(data);

    //todo: update page here.

    document.getElementById('preview').style.display = 'none';
  });

});

$(document).on("click", '.closeDiv', function () {
  document.getElementById('preview').style.display = 'none';
});

/*
var editable = document.getElementById('editable');

addEvent(editable, 'blur', function () {
  // lame that we're hooking the blur event
  localStorage.setItem('contenteditable', this.innerHTML);
  document.designMode = 'off';
});

addEvent(editable, 'focus', function () {
  document.designMode = 'on';
});

addEvent(document.getElementById('clear'), 'click', function () {
  localStorage.clear();
  window.location = window.location; // refresh
});

if (localStorage.getItem('contenteditable')) {
  editable.innerHTML = localStorage.getItem('contenteditable');
}
*/
