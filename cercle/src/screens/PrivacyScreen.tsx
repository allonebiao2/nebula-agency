import React from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { COLORS } from '../lib/config';

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={s.block}>
      <Text style={s.h}>{title}</Text>
      <Text style={s.p}>{children}</Text>
    </View>
  );
}

export default function PrivacyScreen() {
  return (
    <ScrollView style={{ flex: 1, backgroundColor: COLORS.bg }} contentContainerStyle={{ padding: 18 }}>
      <Text style={s.title}>Confidentialité & sécurité</Text>
      <Text style={s.intro}>
        Cercle est conçu pour protéger ses membres — jamais pour espionner. Voici nos règles, sans
        petits caractères.
      </Text>

      <Section title="Vous ne partagez que ce que vous voulez">
        Votre position n’est partagée qu’avec les membres des cercles que vous avez rejoints
        vous-même, et seulement quand vous activez « Partager ma position ». Vous pouvez l’arrêter à
        tout moment.
      </Section>

      <Section title="Pas de pistage caché">
        Il est impossible de suivre quelqu’un à son insu. Chacun voit qui fait partie du cercle, et
        chacun choisit de partager ou non. Cercle n’est pas un outil d’espionnage d’un conjoint ou
        d’un adulte sans son accord — c’est interdit par notre règle absolue.
      </Section>

      <Section title="Qui voit votre position">
        Uniquement les personnes avec qui vous partagez un cercle. Personne d’autre. Techniquement,
        la base de données refuse l’accès à toute autre personne.
      </Section>

      <Section title="Alerte Disparition">
        Quand vous signalez une disparition, les informations (photo, lieu, description) sont
        visibles par la communauté Cercle pour aider aux recherches. Ne publiez que des
        informations exactes et le signalement aux autorités reste recommandé.
      </Section>

      <Section title="Vos données">
        Vous pouvez modifier vos informations ou supprimer définitivement votre compte (et toutes
        vos données) à tout moment depuis votre profil.
      </Section>

      <Text style={s.footer}>Cercle — NEBULA Agency · Cotonou, Bénin</Text>
    </ScrollView>
  );
}

const s = StyleSheet.create({
  title: { color: COLORS.text, fontSize: 24, fontWeight: '800' },
  intro: { color: COLORS.muted, marginTop: 10, marginBottom: 18, lineHeight: 20 },
  block: {
    backgroundColor: COLORS.card,
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  h: { color: COLORS.text, fontWeight: '700', fontSize: 16, marginBottom: 8 },
  p: { color: COLORS.muted, lineHeight: 21, fontSize: 14 },
  footer: { color: COLORS.muted, textAlign: 'center', marginTop: 18, marginBottom: 10, fontSize: 12 },
});
