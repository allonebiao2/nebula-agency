import React, { useEffect, useState } from 'react';
import {
  Alert,
  Linking,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { deleteMyAccount, getMyProfile, updateMyProfile } from '../lib/api';
import { COLORS } from '../lib/config';
import { supabase } from '../lib/supabase';

export default function ProfileScreen() {
  const { signOut } = useAuth();
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setEmail(data.user?.email ?? ''));
    getMyProfile().then((p) => {
      if (p) {
        setName(p.display_name ?? '');
        setPhone(p.phone ?? '');
      }
    });
  }, []);

  const save = async () => {
    if (!name.trim()) {
      Alert.alert('Nom requis', 'Entrez votre nom.');
      return;
    }
    setSaving(true);
    try {
      await updateMyProfile(name, phone || null);
      Alert.alert('Enregistré', 'Votre profil a été mis à jour.');
    } catch (e: any) {
      Alert.alert('Erreur', e?.message ?? '');
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = () => {
    Alert.alert(
      'Supprimer mon compte',
      'Cette action est définitive : votre compte, vos cercles et vos positions seront effacés.',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Supprimer',
          style: 'destructive',
          onPress: async () => {
            try {
              await deleteMyAccount();
              await signOut();
            } catch (e: any) {
              Alert.alert('Erreur', e?.message ?? '');
            }
          },
        },
      ],
    );
  };

  return (
    <ScrollView style={{ flex: 1, backgroundColor: COLORS.bg }} contentContainerStyle={{ padding: 16 }}>
      <View style={s.avatar}>
        <Text style={s.avatarText}>{(name || '?').charAt(0).toUpperCase()}</Text>
      </View>
      <Text style={s.email}>{email}</Text>

      <View style={s.card}>
        <Text style={s.label}>Nom affiché</Text>
        <TextInput style={s.input} value={name} onChangeText={setName} placeholderTextColor={COLORS.muted} />

        <Text style={s.label}>Téléphone (optionnel)</Text>
        <TextInput
          style={s.input}
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
          placeholder="Ex : 97 00 00 00"
          placeholderTextColor={COLORS.muted}
        />

        <TouchableOpacity style={s.btn} onPress={save} disabled={saving}>
          <Text style={s.btnText}>{saving ? 'Enregistrement…' : 'Enregistrer'}</Text>
        </TouchableOpacity>
      </View>

      <TouchableOpacity
        style={s.row}
        onPress={() => Linking.openURL('https://nebula-agency.online/cercle/confidentialite')}
      >
        <Text style={s.rowText}>Confidentialité & sécurité</Text>
        <Text style={s.chevron}>›</Text>
      </TouchableOpacity>

      <TouchableOpacity style={s.logout} onPress={signOut}>
        <Text style={s.logoutText}>Se déconnecter</Text>
      </TouchableOpacity>

      <TouchableOpacity style={s.delete} onPress={confirmDelete}>
        <Text style={s.deleteText}>Supprimer mon compte</Text>
      </TouchableOpacity>

      <Text style={s.version}>Cercle — NEBULA Agency</Text>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  avatar: {
    width: 84,
    height: 84,
    borderRadius: 42,
    backgroundColor: COLORS.accent,
    alignSelf: 'center',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
  },
  avatarText: { color: '#fff', fontSize: 36, fontWeight: '800' },
  email: { color: COLORS.muted, textAlign: 'center', marginTop: 10, marginBottom: 20 },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  label: { color: COLORS.muted, marginBottom: 6, marginTop: 12, fontSize: 13 },
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
    paddingVertical: 13,
    alignItems: 'center',
    marginTop: 16,
  },
  btnText: { color: '#fff', fontWeight: '700' },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: COLORS.card,
    borderRadius: 12,
    padding: 16,
    marginTop: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  rowText: { color: COLORS.text, fontSize: 15, fontWeight: '600' },
  chevron: { color: COLORS.muted, fontSize: 22 },
  logout: { padding: 16, alignItems: 'center', marginTop: 18 },
  logoutText: { color: COLORS.text, fontWeight: '700' },
  delete: { padding: 12, alignItems: 'center' },
  deleteText: { color: COLORS.danger, fontWeight: '600' },
  version: { color: COLORS.muted, textAlign: 'center', marginTop: 24, fontSize: 12 },
});
