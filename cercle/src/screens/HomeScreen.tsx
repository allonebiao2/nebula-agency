import React, { useCallback, useState } from 'react';
import { useFocusEffect } from '@react-navigation/native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import {
  Alert,
  FlatList,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import type { CerclesStackParamList, Circle } from '../types';
import { createCircle, getMyCircles, joinCircle } from '../lib/api';
import { COLORS } from '../lib/config';

type Props = NativeStackScreenProps<CerclesStackParamList, 'CerclesList'>;

export default function HomeScreen({ navigation }: Props) {
  const [circles, setCircles] = useState<Circle[]>([]);
  const [newName, setNewName] = useState('');
  const [code, setCode] = useState('');
  const [busy, setBusy] = useState(false);

  const load = useCallback(() => {
    getMyCircles()
      .then(setCircles)
      .catch((e) => Alert.alert('Erreur', e?.message ?? ''));
  }, []);

  useFocusEffect(useCallback(() => load(), [load]));

  const doCreate = async () => {
    if (!newName.trim()) return;
    setBusy(true);
    try {
      const c = await createCircle(newName.trim());
      setNewName('');
      load();
      navigation.navigate('CircleDetail', { circleId: c.id, name: c.name, inviteCode: c.invite_code });
    } catch (e: any) {
      Alert.alert('Erreur', e?.message ?? '');
    } finally {
      setBusy(false);
    }
  };

  const doJoin = async () => {
    if (!code.trim()) return;
    setBusy(true);
    try {
      const c = await joinCircle(code);
      setCode('');
      load();
      navigation.navigate('CircleDetail', { circleId: c.id, name: c.name, inviteCode: c.invite_code });
    } catch (e: any) {
      Alert.alert('Code invalide', e?.message ?? '');
    } finally {
      setBusy(false);
    }
  };

  return (
    <View style={s.wrap}>
      <FlatList
        data={circles}
        keyExtractor={(c) => c.id}
        ListHeaderComponent={
          <View>
            <View style={s.box}>
              <Text style={s.boxTitle}>Créer un cercle</Text>
              <TextInput
                style={s.input}
                placeholder="Ex : Famille, Enfants…"
                placeholderTextColor={COLORS.muted}
                value={newName}
                onChangeText={setNewName}
              />
              <TouchableOpacity style={s.btn} onPress={doCreate} disabled={busy}>
                <Text style={s.btnText}>Créer</Text>
              </TouchableOpacity>
            </View>

            <View style={s.box}>
              <Text style={s.boxTitle}>Rejoindre avec un code</Text>
              <TextInput
                style={s.input}
                placeholder="Ex : 9F3A2B"
                placeholderTextColor={COLORS.muted}
                autoCapitalize="characters"
                value={code}
                onChangeText={setCode}
              />
              <TouchableOpacity style={[s.btn, s.btnAlt]} onPress={doJoin} disabled={busy}>
                <Text style={s.btnText}>Rejoindre</Text>
              </TouchableOpacity>
            </View>

            <Text style={s.section}>Mes cercles</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={s.circle}
            onPress={() =>
              navigation.navigate('CircleDetail', {
                circleId: item.id,
                name: item.name,
                inviteCode: item.invite_code,
              })
            }
          >
            <Text style={s.circleName}>◍ {item.name}</Text>
            <Text style={s.circleCode}>Code : {item.invite_code}</Text>
          </TouchableOpacity>
        )}
        ListEmptyComponent={<Text style={s.empty}>Aucun cercle pour l’instant.</Text>}
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
      />
    </View>
  );
}

const s = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: COLORS.bg },
  box: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  boxTitle: { color: COLORS.text, fontWeight: '700', fontSize: 16, marginBottom: 10 },
  input: {
    backgroundColor: COLORS.bg,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 11,
    color: COLORS.text,
    fontSize: 15,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  btn: {
    backgroundColor: COLORS.accent,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 12,
  },
  btnAlt: { backgroundColor: COLORS.accentSoft },
  btnText: { color: '#fff', fontWeight: '700' },
  section: { color: COLORS.muted, fontWeight: '700', marginVertical: 10, fontSize: 13 },
  circle: {
    backgroundColor: COLORS.card,
    borderRadius: 14,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  circleName: { color: COLORS.text, fontSize: 17, fontWeight: '700' },
  circleCode: { color: COLORS.muted, marginTop: 4, fontSize: 13 },
  empty: { color: COLORS.muted, textAlign: 'center', marginTop: 10 },
  logout: { padding: 16, alignItems: 'center' },
  logoutText: { color: COLORS.muted },
});
