// Variables publiques chargées depuis .env (Expo lit automatiquement EXPO_PUBLIC_*).
// La clé ANON est sûre côté client : la confidentialité est garantie par les
// policies RLS de Supabase. NE JAMAIS mettre la clé service_role ici.
export const SUPABASE_URL = process.env.EXPO_PUBLIC_SUPABASE_URL ?? '';
export const SUPABASE_ANON_KEY = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY ?? '';

export const isConfigured = () => Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

// Palette Cercle
export const COLORS = {
  bg: '#0E1B33',
  card: '#16264a',
  accent: '#3B82F6',
  accentSoft: '#1d3a6b',
  text: '#F8FAFC',
  muted: '#9FB3D1',
  danger: '#EF4444',
  ok: '#22C55E',
  border: '#24395f',
};
