/// <reference lib="dom" />
import React, { useEffect, useRef } from 'react';
import type { MemberLoc } from '../types';

// WEB : on charge Leaflet depuis le CDN une fois, puis on affiche une carte OSM dans un div.
let leafletPromise: Promise<any> | null = null;
function loadLeaflet(): Promise<any> {
  const w = window as any;
  if (w.L) return Promise.resolve(w.L);
  if (leafletPromise) return leafletPromise;
  leafletPromise = new Promise((resolve, reject) => {
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    document.head.appendChild(css);
    const sc = document.createElement('script');
    sc.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    sc.onload = () => resolve((window as any).L);
    sc.onerror = reject;
    document.body.appendChild(sc);
  });
  return leafletPromise;
}

export default function LeafletMap({ members }: { members: MemberLoc[] }) {
  const divRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<any>(null);
  const markersRef = useRef<Record<string, any>>({});
  const fittedRef = useRef(false);

  const update = (L: any) => {
    const map = mapRef.current;
    if (!map) return;
    const markers = markersRef.current;
    const bounds: any[] = [];
    members.forEach((m) => {
      if (m.lat == null) return;
      const ll = [m.lat, m.lng];
      bounds.push(ll);
      if (markers[m.user_id]) markers[m.user_id].setLatLng(ll).setPopupContent(m.display_name);
      else markers[m.user_id] = L.marker(ll).addTo(map).bindPopup(m.display_name);
    });
    Object.keys(markers).forEach((id) => {
      if (!members.some((x) => x.user_id === id && x.lat != null)) {
        map.removeLayer(markers[id]);
        delete markers[id];
      }
    });
    if (!fittedRef.current && bounds.length === 1) {
      map.setView(bounds[0], 15);
      fittedRef.current = true;
    } else if (!fittedRef.current && bounds.length > 1) {
      map.fitBounds(bounds, { padding: [40, 40] });
      fittedRef.current = true;
    }
  };

  useEffect(() => {
    let cancelled = false;
    loadLeaflet().then((L) => {
      if (cancelled || !divRef.current || mapRef.current) return;
      mapRef.current = L.map(divRef.current, {
        zoomControl: true,
        attributionControl: false,
      }).setView([6.3703, 2.3912], 12);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(
        mapRef.current,
      );
      update(L);
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const L = (window as any).L;
    if (L && mapRef.current) update(L);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [members]);

  return (
    <div
      ref={divRef}
      style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, background: '#0E1B33' }}
    />
  );
}
