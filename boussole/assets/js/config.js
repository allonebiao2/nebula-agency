// Boussole — configuration
// Nom de l'appli (centralisé : changer ici + index.html + manifest.webmanifest).
export const APP_NAME = 'Boussole';

// Version de l'appli : sert au cache-busting (bumper à chaque modif).
export const APP_VERSION = '20260710d';

// --- Supabase (mode cloud) ---
// Laisser vide = l'appli tourne en MODE LOCAL (localStorage, hors-ligne, privé à l'appareil).
// Renseigner ces 2 valeurs = active la synchro cloud multi-appareils (mobile <-> PC).
// La clé "anon" est PUBLIQUE et sûre côté client : la sécurité est assurée par la
// Row-Level Security de Supabase (chaque commerçant ne voit QUE ses données).
export const SUPABASE_URL = 'https://xukduhqqfzogisoimhyo.supabase.co';
export const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh1a2R1aHFxZnpvZ2lzb2ltaHlvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM1Mjc4MDMsImV4cCI6MjA5OTEwMzgwM30.nTmpJarpRzteBTSoirlGZub5RgTkYUE_P15vLqluDG0';

export const CLOUD_ENABLED = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

// Devise par défaut (FCFA). La devise active est dans profil.devise (multi-devises).
export const DEVISE = 'F';
export const DEVISE_LONG = 'FCFA';

// Devises supportées (Afrique + courantes). Clé = code stocké dans profil.devise.
export const CURRENCIES = {
  'F':   { symbol: 'F',   label: 'Franc CFA — FCFA', pos: 'after' },
  'NGN': { symbol: '₦',   label: 'Naira — Nigeria', pos: 'before' },
  'GHS': { symbol: '₵',   label: 'Cedi — Ghana', pos: 'before' },
  'GNF': { symbol: 'FG',  label: 'Franc guinéen', pos: 'after' },
  'KES': { symbol: 'Ksh', label: 'Shilling — Kenya', pos: 'before' },
  'USD': { symbol: '$',   label: 'Dollar US', pos: 'before' },
  'EUR': { symbol: '€',   label: 'Euro', pos: 'after' },
};
