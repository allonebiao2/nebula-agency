import React, { useEffect, useRef } from 'react';
import { WebView } from 'react-native-webview';
import type { MemberLoc } from '../types';

// MOBILE : Leaflet + tuiles OpenStreetMap dans une WebView (aucune clé, aucun Google, aucune CB).
const HTML = `<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>html,body,#map{height:100%;margin:0;background:#0E1B33}</style>
</head>
<body>
<div id="map"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
  var map = L.map('map', { zoomControl: true, attributionControl: false }).setView([6.3703, 2.3912], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
  var markers = {};
  var fitted = false;
  function setMarkers(list){
    var bounds = [];
    list.forEach(function(m){
      if (m.lat == null) return;
      var ll = [m.lat, m.lng];
      bounds.push(ll);
      if (markers[m.user_id]) { markers[m.user_id].setLatLng(ll).setPopupContent(m.display_name); }
      else { markers[m.user_id] = L.marker(ll).addTo(map).bindPopup(m.display_name); }
    });
    Object.keys(markers).forEach(function(id){
      var still = list.some(function(x){ return x.user_id === id && x.lat != null; });
      if (!still){ map.removeLayer(markers[id]); delete markers[id]; }
    });
    if (!fitted && bounds.length === 1) { map.setView(bounds[0], 15); fitted = true; }
    else if (!fitted && bounds.length > 1) { map.fitBounds(bounds, { padding: [40,40] }); fitted = true; }
  }
  window.__setMarkers = setMarkers;
  document.body.dataset.ready = '1';
</script>
</body>
</html>`;

export default function LeafletMap({ members }: { members: MemberLoc[] }) {
  const ref = useRef<WebView>(null);

  const push = () => {
    const json = JSON.stringify(
      members.map((m) => ({
        user_id: m.user_id,
        display_name: m.display_name,
        lat: m.lat,
        lng: m.lng,
      })),
    );
    ref.current?.injectJavaScript(`window.__setMarkers && window.__setMarkers(${json}); true;`);
  };

  useEffect(push, [members]);

  return (
    <WebView
      ref={ref}
      originWhitelist={['*']}
      source={{ html: HTML }}
      onLoadEnd={push}
      style={{ flex: 1, backgroundColor: '#0E1B33' }}
      javaScriptEnabled
      domStorageEnabled
    />
  );
}
