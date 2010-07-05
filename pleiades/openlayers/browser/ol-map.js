var map, base, vectors, drawControls, selectControl, selectedFeature;

function getJSON() {
    var documentNode = document;
    var linkNode = documentNode.evaluate(
                    '//link[@rel="alternate" and @type="application/json"]',
                    documentNode,
                    null,
                    XPathResult.FIRST_ORDERED_NODE_TYPE,
                    null
                    ).singleNodeValue;
    var jsonURI = linkNode.getAttribute("href");
    return jsonURI;
}

function onPopupClose(evt) {
    selectControl.unselect(selectedFeature);
}

function onFeatureSelect(feature) {
    selectedFeature = feature;
    var p = feature.attributes;
    var popup = new OpenLayers.Popup.FramedCloud("chicken", 
                             feature.geometry.getBounds().getCenterLonLat(),
                             null,
                             '<div style="font-size:.8em;height:3em;"><p>Feature: <a href="' + p.link + '">' + p.title + '</a></p><p>' + p.description + '</p></div>',
                             null, true, onPopupClose);
    feature.popup = popup;
    map.addPopup(popup);
}

function onFeatureUnselect(feature) {
    map.removePopup(feature.popup);
    feature.popup.destroy();
    feature.popup = null;
}

function initMap() {

  map = new OpenLayers.Map('map', {
    projection: new OpenLayers.Projection("EPSG:900913"),
    displayProjection: new OpenLayers.Projection("EPSG:4326"),
    units: "m",
    numZoomLevels: 18,
    maxResolution: 156543.0339,
    maxExtent: new OpenLayers.Bounds(-20037508, -20037508, 20037508, 20037508)
    });

  base = new OpenLayers.Layer.Google('Base', {   
    isBaseLayer: true,
    type: G_PHYSICAL_MAP, 
    sphericalMercator: true
    });

  var jsonURI = getJSON();
  
  var template = {
    fillColor: "${getColor}", 
    strokeColor: "${getColor}", 
    fillOpacity: "${getOpacity}",
    strokeOpacity: 1.0,
    pointRadius: 5 };
  
  var context = {
    getColor: function(feature) {
      if (feature.attributes['description'].indexOf('undetermined') > -1) {
        return "orange";
      }
      else {
        return "blue";
      }
    },
    getOpacity: function(feature) {
      if (feature.attributes['description'].indexOf('undetermined') > -1) {
        return 0.2;
      }
      else {
        return 0.8;
      }
    }
  };

  var style = new OpenLayers.Style(template, {context: context});
  var styleMap = new OpenLayers.StyleMap(style);

  vectors = new OpenLayers.Layer.Vector("Place", {
    strategies: [new OpenLayers.Strategy.Fixed()],
    protocol: new OpenLayers.Protocol.HTTP({
      url: jsonURI,
      format: new OpenLayers.Format.GeoJSON()}),
    styleMap: styleMap
    });

  vectors.events.on({'loadend' : function(e) {
    var extent = vectors.getDataExtent();
    extent.left -= 5000.0;
    extent.right += 5000.0;
    extent.top += 5000.0;
    extent.bottom -= 5000.0;
    map.zoomToExtent(extent);
    }});

  map.addLayers([base, vectors]);
  map.addControl(new OpenLayers.Control.MousePosition());
  selectControl = new OpenLayers.Control.SelectFeature(
                      vectors,
                      {onSelect: onFeatureSelect, 
                       onUnselect: onFeatureUnselect});    
  map.addControl(selectControl);
  selectControl.activate();
  map.zoomToMaxExtent();
}

registerPloneFunction(initMap);
