// https://github.com/ariya/phantomjs/blob/master/examples/rasterize.js
// http://stackoverflow.com/questions/11917042/how-to-render-part-of-a-page-with-phantomjs

var page = require('webpage').create(),
    system = require('system'),
    address, output, size;

address = system.args[1];
output = system.args[2];
page.viewportSize = { width: 600, height: 600 };
if (system.args.length > 3 && system.args[2].substr(-4) === ".pdf") {
  size = system.args[3].split('*');
  page.paperSize = size.length === 2 ? { width: size[0], height: size[1], margin: '0px' }
                                     : { format: system.args[3], orientation: 'portrait', margin: '1cm' };
} else if (system.args.length > 3 && system.args[3].substr(-2) === "px") {
    size = system.args[3].split('*');
    if (size.length === 2) {
      pageWidth = parseInt(size[0], 10);
      pageHeight = parseInt(size[1], 10);
      page.viewportSize = { width: pageWidth, height: pageHeight };
      page.clipRect = { top: 0, left: 0, width: pageWidth, height: pageHeight };
    } else {
      console.log("size:", system.args[3]);
      pageWidth = parseInt(system.args[3], 10);
      pageHeight = parseInt(pageWidth * 3/4, 10);
      console.log ("pageHeight:",pageHeight);
      page.viewportSize = { width: pageWidth, height: pageHeight };
    }
}
if (system.args.length > 4) {
    page.zoomFactor = system.args[4];
}
page.open(address, function (status) {
  if (status !== 'success') {
      console.log('Unable to load the address!');
      phantom.exit(1);
  } else {
    window.setTimeout(function () {
      var clipRect = page.evaluate(function() {
        document.querySelector('.leaflet-top').style.display = 'none';
        document.querySelector('.leaflet-right').style.display = 'none';
        document.querySelector('.leaflet-control-attribution').style.display = 'none';
        return document.querySelector('#map').getBoundingClientRect();
      });
      page.clipRect = {
        top: clipRect.top,
        left: clipRect.left,
        width: clipRect.width,
        height: clipRect.height
      };
      page.render(output);
      phantom.exit();
    }, 5200);
  }
});
