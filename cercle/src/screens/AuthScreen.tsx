import React, { useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';
import { useAuth } from '../context/AuthContext';
import { COLORS, isConfigured } from '../lib/config';

type Mode = 'in' | 'up' | 'reset';

export default function AuthScreen() {
  const { signIn, signUp, resetPassword } = useAuth();
  const [mode, setMode] = useState<Mode>('up');
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);

  const emailOk = /^\S+@\S+\.\S+$/.test(email.trim());

  const submit = async () => {
    if (!isConfigured()) {
      Alert.alert('Configuration manquante', 'Le fichier .env (Supabase) n’est pas rempli.');
      return;
    }
    if (!emailOk) {
      Alert.alert('Email invalide', 'Entrez une adresse email valide (ex : nom@gmail.com).');
      return;
    }
    if (mode === 'reset') {
      setBusy(true);
      try {
        await resetPassword(email);
        Alert.alert('Email envoyé', 'Un lien de réinitialisation vous a été envoyé.');
        setMode('in');
      } catch (e: any) {
        Alert.alert('Erreur', e?.message ?? 'Réessayez.');
      } finally {
        setBusy(false);
      }
      return;
    }
    if (password.length < 6 || (mode === 'up' && !name.trim())) {
      Alert.alert('Champs requis', 'Nom (à l’inscription) et mot de passe de 6 caractères min.');
      return;
    }
    setBusy(true);
    try {
      if (mode === 'up') {
        const { needsConfirmation } = await signUp(email, password, name);
        if (needsConfirmation) {
          Alert.alert(
            'Compte créé',
            'Vérifiez votre boîte mail (et les spams) pour confirmer votre adresse, puis connectez-vous.',
          );
          setMode('in');
          setPassword('');
        }
      } else {
        await signIn(email, password);
      }
    } catch (e: any) {
      Alert.alert('Erreur', traduire(e?.message));
    } finally {
      setBusy(false);
    }
  };

  const title =
    mode === 'up' ? 'Créer mon compte' : mode === 'in' ? 'Se connecter' : 'Mot de passe oublié';

  return (
    <KeyboardAvoidingView
      style={{ flex: 1, backgroundColor: COLORS.bg }}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={s.wrap} keyboardShouldPersistTaps="handled">
        <Text style={s.logo}>◍ Cercle</Text>
        <Text style={s.tagline}>Veillez les uns sur les autres.</Text>

        <View style={s.card}>
          <Text style={s.h}>{title}</Text>

          {mode === 'up' && (
            <>
              <Text style={s.label}>Votre nom</Text>
              <TextInput
                style={s.input}
                value={name}
                onChangeText={setName}
                placeholder="Ex : Maman Adjoa"
                placeholderTextColor={COLORS.muted}
              />
            </>
          )}

          <Text style={s.label}>Email</Text>
          <TextInput
            style={s.input}
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
            autoCorrect={false}
            placeholder="nom@gmail.com"
            placeholderTextColor={COLORS.muted}
          />

          {mode !== 'reset' && (
            <>
              <Text style={s.label}>Mot de passe</Text>
              <TextInput
                style={s.input}
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                placeholder="6 caractères minimum"
                placeholderTextColor={COLORS.muted}
              />
            </>
          )}

          <TouchableOpacity style={s.btn} onPress={submit} disabled={busy}>
            {busy ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={s.btnText}>
                {mode === 'up' ? 'Créer mon compte' : mode === 'in' ? 'Se connecter' : 'Envoyer le lien'}
              </Text>
            )}
          </TouchableOpacity>

          {mode === 'in' && (
            <TouchableOpacity onPress={() => setMode('reset')}>
              <Text style={s.link}>Mot de passe oublié ?</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            onPress={() => setMode(mode === 'up' ? 'in' : 'up')}
            style={{ marginTop: 14 }}
          >
            <Text style={s.switch}>
              {mode === 'up'
                ? 'J’ai déjà un compte → Se connecter'
                : 'Nouveau ? → Créer un compte'}
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={s.note}>
          Cercle ne partage votre position qu’avec les membres que vous acceptez. Personne ne peut
          vous suivre à votre insu.
        </Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

function traduire(msg?: string): string {
  if (!msg) return 'Réessayez.';
  if (/Invalid login credentials/i.test(msg)) return 'Email ou mot de passe incorrect.';
  if (/Email not confirmed/i.test(msg)) return 'Confirmez d’abord votre email (vérifiez vos spams).';
  if (/already registered|already exists/i.test(msg)) return 'Cet email a déjà un compte.';
  if (/rate limit|too many/i.test(msg)) return 'Trop de tentatives, réessayez dans quelques minutes.';
  return msg;
}

const s = StyleSheet.create({
  wrap: { padding: 24, paddingTop: 80, flexGrow: 1 },
  logo: { color: COLORS.text, fontSize: 40, fontWeight: '800', textAlign: 'center' },
  tagline: { color: COLORS.muted, textAlign: 'center', marginTop: 6, marginBottom: 28 },
  card: {
    backgroundColor: COLORS.card,
    borderRadius: 18,
    padding: 20,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  h: { color: COLORS.text, fontSize: 20, fontWeight: '700', marginBottom: 14 },
  label: { color: COLORS.muted, marginBottom: 6, marginTop: 12, fontSize: 13 },
  input: {
    backgroundColor: COLORS.bg,
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 12,
    color: COLORS.text,
    fontSize: 16,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  btn: {
    backgroundColor: COLORS.accent,
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 22,
  },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  link: { color: COLORS.muted, textAlign: 'center', marginTop: 16 },
  switch: { color: COLORS.accent, textAlign: 'center' },
  note: { color: COLORS.muted, fontSize: 12, textAlign: 'center', marginTop: 24, lineHeight: 18 },
});
