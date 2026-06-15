import React, { useState } from 'react';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import * as ImagePicker from 'expo-image-picker';
import * as Location from 'expo-location';
import {
  ActivityIndicator,
  Alert,
  Image,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import type { AlertsStackParamList } from '../types';
import { createMissingAlert, uploadAlertPhoto } from '../lib/api';
import { COLORS } from '../lib/config';

type Props = NativeStackScreenProps<AlertsStackParamList, 'ReportMissing'>;

export default function ReportMissingScreen({ navigation }: Props) {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [place, setPlace] = useState('');
  const [lat, setLat] = useState<number | null>(null);
  const [lng, setLng] = useState<number | null>(null);
  const [desc, setDesc] = useState('');
  const [contact, setContact] = useState('');
  const [busy, setBusy] = useState(false);

  const pickPhoto = async () => {
    const r = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.6,
    });
    if (!r.canceled && r.assets[0]) setPhotoUri(r.assets[0].uri);
  };

  const useCurrentLocation = async () => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Position', 'Autorisez la localisation pour enregistrer le dernier lieu vu.');
      return;
    }
    const p = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
    setLat(p.coords.latitude);
    setLng(p.coords.longitude);
    if (!place) setPlace('Position actuelle');
  };

  const submit = async () => {
    if (!name.trim()) {
      Alert.alert('Nom requis', 'Indiquez au moins le nom de la personne.');
      return;
    }
    setBusy(true);
    try {
      let photo_url: string | null = null;
      if (photoUri) photo_url = await uploadAlertPhoto(photoUri);
      await createMissingAlert({
        person_name: name.trim(),
        age: age ? parseInt(age, 10) || null : null,
        photo_url,
        last_seen_lat: lat,
        last_seen_lng: lng,
        last_seen_place: place.trim() || null,
        last_seen_at: new Date().toISOString(),
        description: desc.trim() || null,
        contact_phone: contact.trim() || null,
      });
      Alert.alert('Alerte publiée', 'Merci. La communauté Cercle est prévenue.');
      navigation.goBack();
    } catch (e: any) {
      Alert.alert('Erreur', e?.message ?? 'Réessayez.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: COLORS.bg }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={{ padding: 16 }} keyboardShouldPersistTaps="handled">
        <Text style={s.warn}>
          ⚠️ Signalez aussi la disparition aux autorités. Cercle aide à diffuser, il ne remplace pas
          la police.
        </Text>

        <TouchableOpacity style={s.photoBox} onPress={pickPhoto}>
          {photoUri ? (
            <Image source={{ uri: photoUri }} style={s.photo} />
          ) : (
            <Text style={s.photoText}>＋ Ajouter une photo</Text>
          )}
        </TouchableOpacity>

        <Text style={s.label}>Nom de la personne *</Text>
        <TextInput style={s.input} value={name} onChangeText={setName} placeholderTextColor={COLORS.muted} placeholder="Ex : Koffi A." />

        <Text style={s.label}>Âge</Text>
        <TextInput style={s.input} value={age} onChangeText={setAge} keyboardType="number-pad" placeholderTextColor={COLORS.muted} placeholder="Ex : 8" />

        <Text style={s.label}>Dernier lieu vu</Text>
        <TextInput style={s.input} value={place} onChangeText={setPlace} placeholderTextColor={COLORS.muted} placeholder="Ex : Marché Dantokpa, Cotonou" />
        <TouchableOpacity style={s.locBtn} onPress={useCurrentLocation}>
          <Text style={s.locText}>{lat != null ? '✓ Position enregistrée' : '📍 Utiliser ma position actuelle'}</Text>
        </TouchableOpacity>

        <Text style={s.label}>Description (vêtements, signes…)</Text>
        <TextInput
          style={[s.input, { height: 90, textAlignVertical: 'top' }]}
          value={desc}
          onChangeText={setDesc}
          multiline
          placeholderTextColor={COLORS.muted}
          placeholder="Ex : t-shirt rouge, short bleu, cicatrice au bras gauche…"
        />

        <Text style={s.label}>Téléphone à contacter</Text>
        <TextInput style={s.input} value={contact} onChangeText={setContact} keyboardType="phone-pad" placeholderTextColor={COLORS.muted} placeholder="Ex : 97 00 00 00" />

        <TouchableOpacity style={s.submit} onPress={submit} disabled={busy}>
          {busy ? <ActivityIndicator color="#fff" /> : <Text style={s.submitText}>Publier l’alerte</Text>}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const s = StyleSheet.create({
  warn: { color: COLORS.muted, backgroundColor: COLORS.card, padding: 12, borderRadius: 10, lineHeight: 19, fontSize: 13, marginBottom: 16 },
  photoBox: {
    height: 160,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
    backgroundColor: COLORS.card,
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  photo: { width: '100%', height: '100%' },
  photoText: { color: COLORS.accent, fontWeight: '700' },
  label: { color: COLORS.muted, marginTop: 14, marginBottom: 6, fontSize: 13 },
  input: {
    backgroundColor: COLORS.card,
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 11,
    color: COLORS.text,
    fontSize: 15,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  locBtn: { marginTop: 8, paddingVertical: 10, alignItems: 'center', borderRadius: 10, backgroundColor: COLORS.accentSoft },
  locText: { color: COLORS.text, fontWeight: '600' },
  submit: { backgroundColor: COLORS.danger, borderRadius: 12, paddingVertical: 16, alignItems: 'center', marginTop: 24 },
  submitText: { color: '#fff', fontWeight: '800', fontSize: 16 },
});
