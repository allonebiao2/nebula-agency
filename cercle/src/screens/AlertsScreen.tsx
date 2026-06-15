import React, { useCallback, useEffect, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import {
  Alert,
  FlatList,
  Image,
  Linking,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';
import type { AlertsStackParamList } from '../types';
import { getMissingAlerts, resolveMissingAlert, type MissingAlert } from '../lib/api';
import { supabase } from '../lib/supabase';
import { COLORS } from '../lib/config';

type Props = NativeStackScreenProps<AlertsStackParamList, 'AlertsList'>;

function timeAgo(iso: string | null): string {
  if (!iso) return '';
  const sec = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (sec < 3600) return `il y a ${Math.max(1, Math.floor(sec / 60))} min`;
  if (sec < 86400) return `il y a ${Math.floor(sec / 3600)} h`;
  return `il y a ${Math.floor(sec / 86400)} j`;
}

export default function AlertsScreen({ navigation }: Props) {
  const [alerts, setAlerts] = useState<MissingAlert[]>([]);
  const [myId, setMyId] = useState<string | null>(null);

  const load = useCallback(() => {
    getMissingAlerts()
      .then(setAlerts)
      .catch(() => {});
  }, []);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setMyId(data.user?.id ?? null));
    const ch = supabase
      .channel('missing-all')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'missing_alerts' }, () => load())
      .subscribe();
    return () => {
      supabase.removeChannel(ch);
    };
  }, [load]);

  useFocusEffect(useCallback(() => load(), [load]));

  const markFound = (a: MissingAlert) => {
    Alert.alert('Marquer comme retrouvé(e)', `${a.person_name} a été retrouvé(e) ?`, [
      { text: 'Annuler', style: 'cancel' },
      {
        text: 'Oui, retrouvé(e)',
        onPress: async () => {
          await resolveMissingAlert(a.id);
          load();
        },
      },
    ]);
  };

  return (
    <View style={s.wrap}>
      <FlatList
        data={alerts}
        keyExtractor={(a) => a.id}
        contentContainerStyle={{ padding: 16, paddingBottom: 90 }}
        ListHeaderComponent={
          <Text style={s.lead}>
            Personnes recherchées près de vous. Partagez largement — chaque regard compte.
          </Text>
        }
        renderItem={({ item }) => (
          <View style={s.card}>
            <View style={s.row}>
              {item.photo_url ? (
                <Image source={{ uri: item.photo_url }} style={s.photo} />
              ) : (
                <View style={[s.photo, s.photoEmpty]}>
                  <Text style={{ color: COLORS.muted, fontSize: 26 }}>?</Text>
                </View>
              )}
              <View style={{ flex: 1 }}>
                <Text style={s.name}>
                  {item.person_name}
                  {item.age ? `, ${item.age} ans` : ''}
                </Text>
                {!!item.last_seen_place && <Text style={s.meta}>Vu(e) : {item.last_seen_place}</Text>}
                <Text style={s.meta}>{timeAgo(item.created_at)}</Text>
              </View>
            </View>

            {!!item.description && <Text style={s.desc}>{item.description}</Text>}

            <View style={s.actions}>
              {item.last_seen_lat != null && (
                <TouchableOpacity
                  style={s.act}
                  onPress={() =>
                    Linking.openURL(
                      `https://maps.google.com/?q=${item.last_seen_lat},${item.last_seen_lng}`,
                    )
                  }
                >
                  <Text style={s.actText}>Lieu</Text>
                </TouchableOpacity>
              )}
              {!!item.contact_phone && (
                <TouchableOpacity style={s.act} onPress={() => Linking.openURL(`tel:${item.contact_phone}`)}>
                  <Text style={s.actText}>Appeler</Text>
                </TouchableOpacity>
              )}
              <TouchableOpacity
                style={s.act}
                onPress={() =>
                  Linking.openURL(
                    `https://wa.me/?text=${encodeURIComponent(
                      `🔴 DISPARITION — ${item.person_name}${item.age ? `, ${item.age} ans` : ''}. ` +
                        `${item.last_seen_place ? 'Vu(e) à ' + item.last_seen_place + '. ' : ''}` +
                        `${item.description ?? ''} ${item.contact_phone ? 'Contact : ' + item.contact_phone : ''} (via Cercle)`,
                    )}`,
                  )
                }
              >
                <Text style={s.actText}>Partager</Text>
              </TouchableOpacity>
              {myId === item.reporter_id && (
                <TouchableOpacity style={[s.act, s.found]} onPress={() => markFound(item)}>
                  <Text style={[s.actText, { color: '#fff' }]}>Retrouvé(e)</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        )}
        ListEmptyComponent={
          <Text style={s.empty}>Aucune alerte active. Espérons que ça reste ainsi. 🙏</Text>
        }
      />

      <TouchableOpacity style={s.fab} onPress={() => navigation.navigate('ReportMissing')}>
        <Text style={s.fabText}>＋ Signaler une disparition</Text>
      </TouchableOpacity>
    </View>
  );
}

const s = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: COLORS.bg },
  lead: { color: COLORS.muted, marginBottom: 14, lineHeight: 19 },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  row: { flexDirection: 'row', gap: 12 },
  photo: { width: 72, height: 72, borderRadius: 12, backgroundColor: COLORS.bg },
  photoEmpty: { alignItems: 'center', justifyContent: 'center' },
  name: { color: COLORS.text, fontSize: 17, fontWeight: '800' },
  meta: { color: COLORS.muted, marginTop: 3, fontSize: 13 },
  desc: { color: COLORS.text, marginTop: 12, lineHeight: 20, fontSize: 14 },
  actions: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginTop: 14 },
  act: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.bg,
  },
  actText: { color: COLORS.accent, fontWeight: '700', fontSize: 13 },
  found: { backgroundColor: COLORS.ok, borderColor: COLORS.ok },
  empty: { color: COLORS.muted, textAlign: 'center', marginTop: 40, lineHeight: 20 },
  fab: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 16,
    backgroundColor: COLORS.danger,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
  },
  fabText: { color: '#fff', fontWeight: '800', fontSize: 16 },
});
