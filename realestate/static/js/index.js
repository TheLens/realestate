/*
 * GET call for /realestate/search
 */
function doSearch(category) {
  var data = prepareData(category);
  var query_string = buildQueryString(data);
  query_string = "/realestate/search" + query_string;
  window.location.href = query_string;
}

// Don't show asterisk info on homepage, since no sales are shown.
document.getElementById('asterisk-note').style.display = 'none';
document.getElementById('cross-note').style.display = 'none';
