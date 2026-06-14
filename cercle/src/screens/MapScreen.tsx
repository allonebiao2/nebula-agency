import React, { useCallback, useEffect, useState } from 'react';
import { Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { MemberLoc } from '../types';
import { getVisibleMembers } from '../lib/api';
import { startSharing, stopSharing, isSharing } from '../lib/location';
import { supabase } from '../lib/supabase';
import { COLORS } from '../lib/config';
import LeafletMap from '../components/LeafletMap';

export default function MapScreen() {
  const insets = useSafeAreaInsets();
  const [members, setMembers] = useState<MemberLoc[]>([]);
  const [sharing, setSharing] = useState(isSharing());

  const load = useCallback(() => {
    getVisibleMembers()
      .then(setMembers)
      .catch(() => {});
  }, []);

  useEffect(() => {
    load();
    const ch = supabase
      .channel('loc-all')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'locations' }, () => load())
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
      Alert.alert(
        'Autorisation refusée',
        'Activez la localisation pour partager votre position avec votre cercle.',
      );
      return;
    }
    setSharing(true);
    setTimeout(load, 1500);
  };

  const withLoc = members.filter((m) => m.lat != null).length;

  return (
    <View style={{ flex: 1, backgroundColor: COLORS.bg }}>
      <LeafletMap members={members} />

      <View style={[s.topBadge, { top: insets.top + 8 }]}>
        <Text style={s.topText}>
          {withLoc} membre{withLoc > 1 ? 's' : ''} en ligne
        </Text>
      </View>

      <View style={[s.bottom, { paddingBottom: insets.bottom + 12 }]}>
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
  bottom: { position: 'absolute', left: 0, right: 0, bottom: 0, paddingHorizontal: 16 },
  share: { borderRadius: 14, paddingVertical: 16, alignItems: 'center' },
  shareOn: { backgroundColor: COLORS.ok },
  shareOff: { backgroundColor: COLORS.accent },
  shareText: { color: '#fff', fontWeight: '800', fontSize: 16 },
});
