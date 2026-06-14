import React, { useCallback, useEffect, useState } from 'react';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import {
  Alert,
  FlatList,
  Linking,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { CerclesStackParamList, MemberLoc } from '../types';
import { getMembersWithLocations } from '../lib/api';
import { supabase } from '../lib/supabase';
import { COLORS } from '../lib/config';

type Props = NativeStackScreenProps<CerclesStackParamList, 'CircleDetail'>;

function timeAgo(iso: string | null): string {
  if (!iso) return 'jamais';
  const sec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (sec < 60) return 'à l’instant';
  if (sec < 3600) return `il y a ${Math.floor(sec / 60)} min`;
  if (sec < 86400) return `il y a ${Math.floor(sec / 3600)} h`;
  return `il y a ${Math.floor(sec / 86400)} j`;
}

export default function CircleScreen({ route }: Props) {
  const { circleId, name, inviteCode } = route.params;
  const [members, setMembers] = useState<MemberLoc[]>([]);

  const load = useCallback(() => {
    getMembersWithLocations(circleId)
      .then(setMembers)
      .catch(() => {});
  }, [circleId]);

  useEffect(() => {
    load();
    const ch = supabase
      .channel(`loc-${circleId}`)
      .on('postgres_changes', { event: '*', schema: 'public', table: 'locations' }, () => load())
      .subscribe();
    const t = setInterval(load, 20000);
    return () => {
      supabase.removeChannel(ch);
      clearInterval(t);
    };
  }, [circleId, load]);

  const invite = () => {
    const msg =
      `Rejoins notre cercle "${name}" sur Cercle (sécurité familiale).\n` +
      `Code d’invitation : ${inviteCode}\n` +
      `On veille les uns sur les autres.`;
    Linking.openURL(`https://wa.me/?text=${encodeURIComponent(msg)}`).catch(() =>
      Alert.alert('Code d’invitation', inviteCode),
    );
  };

  return (
    <View style={s.wrap}>
      <View style={s.header}>
        <Text style={s.title}>◍ {name}</Text>
        <Text style={s.code}>Code d’invitation : {inviteCode}</Text>
      </View>

      <View style={s.actions}>
        <TouchableOpacity style={s.invite} onPress={invite}>
          <Text style={s.inviteText}>Inviter via WhatsApp</Text>
        </TouchableOpacity>
      </View>

      <Text style={s.section}>Membres</Text>
      <FlatList
        data={members}
        keyExtractor={(m) => m.user_id}
        renderItem={({ item }) => (
          <View style={s.member}>
            <View style={[s.dot, { backgroundColor: item.lat != null ? COLORS.ok : COLORS.muted }]} />
            <View style={{ flex: 1 }}>
              <Text style={s.mName}>{item.display_name}</Text>
              <Text style={s.mMeta}>
                {item.lat != null
                  ? `${item.lat.toFixed(5)}, ${item.lng!.toFixed(5)} · ${timeAgo(item.updated_at)}`
                  : 'position non partagée'}
              </Text>
            </View>
            {item.lat != null && (
              <TouchableOpacity
                onPress={() =>
                  Linking.openURL(`https://maps.google.com/?q=${item.lat},${item.lng}`)
                }
              >
                <Text style={s.mapLink}>Carte</Text>
              </TouchableOpacity>
            )}
          </View>
        )}
        ListEmptyComponent={<Text style={s.empty}>Chargement…</Text>}
        contentContainerStyle={{ paddingBottom: 40 }}
      />
    </View>
  );
}

const s = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: COLORS.bg, padding: 16 },
  header: { marginBottom: 14 },
  title: { color: COLORS.text, fontSize: 22, fontWeight: '800' },
  code: { color: COLORS.muted, marginTop: 4 },
  actions: { flexDirection: 'row', gap: 10, marginBottom: 18 },
  share: { flex: 1, borderRadius: 12, paddingVertical: 14, alignItems: 'center' },
  shareOn: { backgroundColor: COLORS.ok },
  shareOff: { backgroundColor: COLORS.accentSoft },
  shareText: { color: '#fff', fontWeight: '700' },
  invite: {
    flex: 1,
    borderRadius: 12,
    paddingVertical: 14,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.card,
  },
  inviteText: { color: COLORS.accent, fontWeight: '700' },
  section: { color: COLORS.muted, fontWeight: '700', marginBottom: 8, fontSize: 13 },
  member: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  dot: { width: 12, height: 12, borderRadius: 6, marginRight: 12 },
  mName: { color: COLORS.text, fontWeight: '700', fontSize: 16 },
  mMeta: { color: COLORS.muted, marginTop: 3, fontSize: 13 },
  mapLink: { color: COLORS.accent, fontWeight: '700' },
  empty: { color: COLORS.muted, textAlign: 'center', marginTop: 20 },
});
