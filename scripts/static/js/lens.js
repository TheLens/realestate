function changeBannerImage() {
  var header_img;
  var screenWidth = document.documentElement.clientWidth;

  if (screenWidth <= 500) {
    header_img = 'https://s3-us-west-2.amazonaws.com/lensnola/land-records/css/images/lens-logo-magnifying-glass-only.png';
    document.getElementById('banner-image').src = header_img;
    document.getElementById('banner-image').width = '35';
    document.getElementById('banner-logo').style.width = '40px';
    document.getElementById('banner-logo').style.marginTop = '0px';
  } else {
    header_img = 'https://s3-us-west-2.amazonaws.com/lensnola/land-records/css/images/lens-logo-retina.png';
    document.getElementById('banner-image').src = header_img;
    document.getElementById('banner-image').width = '100';
    document.getElementById('banner-logo').style.width = '100px';
    document.getElementById('banner-logo').style.marginTop = '5px';
  }
}

window.addEventListener('resize', function(e) {
  changeBannerImage();
});
window.onload = changeBannerImage();
