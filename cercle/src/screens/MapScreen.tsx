import React, { useCallback, useEffect, useState } from 'react';
import { Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import * as Location from 'expo-location';
import type { MemberLoc } from '../types';
import {
  getVisibleMembers,
  getActiveSOS,
  createSOS,
  resolveSOS,
  type SosAlert,
} from '../lib/api';
import { startSharing, stopSharing, isSharing } from '../lib/location';
import { supabase } from '../lib/supabase';
import { COLORS } from '../lib/config';
import LeafletMap from '../components/LeafletMap';

export default function MapScreen() {
  const insets = useSafeAreaInsets();
  const [members, setMembers] = useState<MemberLoc[]>([]);
  const [sharing, setSharing] = useState(isSharing());
  const [sos, setSos] = useState<SosAlert[]>([]);
  const [myId, setMyId] = useState<string | null>(null);

  const load = useCallback(() => {
    getVisibleMembers().then(setMembers).catch(() => {});
    getActiveSOS().then(setSos).catch(() => {});
  }, []);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setMyId(data.user?.id ?? null));
    load();
    const ch = supabase
      .channel('map-live')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'locations' }, () => load())
      .on('postgres_changes', { event: '*', schema: 'public', table: 'sos_alerts' }, () => load())
      .subscribe();
    const t = setInterval(load, 20000);
    return () => {
      supabase.removeChannel(ch);
      clearInterval(t);
    };
  }, [load]);

  const toggleShare = async () => {
    if (sharing) {
      stopSharing();
      setSharing(false);
      return;
    }
    const ok = await startSharing();
    if (!ok) {
      Alert.alert('Autorisation refusée', 'Activez la localisation pour partager votre position.');
      return;
    }
    setSharing(true);
    setTimeout(load, 1500);
  };

  const triggerSOS = () => {
    Alert.alert('Envoyer un SOS', 'Tous les membres de vos cercles seront alertés de votre urgence.', [
      { text: 'Annuler', style: 'cancel' },
      {
        text: 'Envoyer le SOS',
        style: 'destructive',
        onPress: async () => {
          let lat: number | null = null;
          let lng: number | null = null;
          try {
            const { status } = await Location.requestForegroundPermissionsAsync();
            if (status === 'granted') {
              const p = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.High });
              lat = p.coords.latitude;
              lng = p.coords.longitude;
            }
          } catch {}
          try {
            await createSOS(lat, lng);
            Alert.alert('SOS envoyé', 'Vos proches sont prévenus.');
            load();
          } catch (e: any) {
            Alert.alert('Erreur', e?.message ?? '');
          }
        },
      },
    ]);
  };

  const withLoc = members.filter((m) => m.lat != null).length;

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.bg }}>
      <LeafletMap members={members} />

      {/* Bannières SOS actives */}
      <View style={[s.sosBanners, { top: insets.top + 8 }]}>
        {sos.map((a) => (
          <View key={a.id} style={s.sosBanner}>
            <Text style={s.sosBannerText}>
              🚨 SOS — {a.user_id === myId ? 'vous' : a.display_name ?? 'un proche'}
            </Text>
            {a.user_id === myId ? (
              <TouchableOpacity onPress={() => resolveSOS(a.id).then(load)}>
                <Text style={s.sosResolve}>Annuler</Text>
              </TouchableOpacity>
            ) : a.lat != null ? (
              <Text style={s.sosCoord}>
                {a.lat.toFixed(4)}, {a.lng!.toFixed(4)}
              </Text>
            ) : null}
          </View>
        ))}
      </View>

      {sos.length === 0 && (
        <View style={[s.topBadge, { top: insets.top + 8 }]}>
          <Text style={s.topText}>
            {withLoc} membre{withLoc > 1 ? 's' : ''} en ligne
          </Text>
        </View>
      )}

      <View style={[s.bottom, { paddingBottom: insets.bottom + 12 }]}>
        <TouchableOpacity style={s.sosBtn} onPress={triggerSOS} activeOpacity={0.85}>
          <Text style={s.sosBtnText}>SOS</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[s.share, sharing ? s.shareOn : s.shareOff]}
          onPress={toggleShare}
          activeOpacity={0.85}
        >
          <Text style={s.shareText}>
            {sharing ? '●  Je partage ma position' : '○  Partager ma position'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const s = StyleSheet.create({
  topBadge: {
    position: 'absolute',
    alignSelf: 'center',
    backgroundColor: COLORS.card,
    paddingHorizontal: 14,
    paddingVertical: 7,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  topText: { color: COLORS.text, fontWeight: '700', fontSize: 13 },
  sosBanners: { position: 'absolute', left: 12, right: 12, gap: 8 },
  sosBanner: {
    backgroundColor: COLORS.danger,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  sosBannerText: { color: '#fff', fontWeight: '800' },
  sosResolve: { color: '#fff', textDecorationLine: 'underline', fontWeight: '700' },
  sosCoord: { color: '#fff', fontSize: 12 },
  bottom: { position: 'absolute', left: 0, right: 0, bottom: 0, paddingHorizontal: 16, gap: 10 },
  sosBtn: {
    alignSelf: 'flex-end',
    backgroundColor: COLORS.danger,
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.3,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 3 },
    elevation: 6,
  },
  sosBtnText: { color: '#fff', fontWeight: '900', fontSize: 18 },
  share: { borderRadius: 14, paddingVertical: 16, alignItems: 'center' },
  shareOn: { backgroundColor: COLORS.ok },
  shareOff: { backgroundColor: COLORS.accent },
  shareText: { color: '#fff', fontWeight: '800', fontSize: 16 },
});
