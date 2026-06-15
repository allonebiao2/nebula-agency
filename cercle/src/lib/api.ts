import { supabase } from './supabase';
import type { Circle, MemberLoc } from '../types';

export async function getMyCircles(): Promise<Circle[]> {
  const { data, error } = await supabase
    .from('circles')
    .select('*')
    .order('created_at', { ascending: true });
  if (error) throw error;
  return (data ?? []) as Circle[];
}

export async function createCircle(name: string): Promise<Circle> {
  const { data, error } = await supabase.rpc('create_circle', { p_name: name });
  if (error) throw error;
  return data as Circle;
}

export async function joinCircle(code: string): Promise<Circle> {
  const { data, error } = await supabase.rpc('join_circle', { p_code: code.trim() });
  if (error) throw error;
  return data as Circle;
}

export async function getMembersWithLocations(circleId: string): Promise<MemberLoc[]> {
  const { data: members, error } = await supabase
    .from('circle_members')
    .select('user_id')
    .eq('circle_id', circleId);
  if (error) throw error;
  const ids = (members ?? []).map((m: any) => m.user_id);
  if (ids.length === 0) return [];

  const { data: profiles } = await supabase
    .from('profiles')
    .select('id, display_name, phone')
    .in('id', ids);
  const { data: locs } = await supabase
    .from('locations')
    .select('*')
    .in('user_id', ids);

  const locMap = new Map((locs ?? []).map((l: any) => [l.user_id, l]));
  return (profiles ?? []).map((p: any): MemberLoc => {
    const l: any = locMap.get(p.id);
    return {
      user_id: p.id,
      display_name: p.display_name,
      phone: p.phone,
      lat: l?.lat ?? null,
      lng: l?.lng ?? null,
      accuracy: l?.accuracy ?? null,
      updated_at: l?.updated_at ?? null,
    };
  });
}

// Tous les membres que j'ai le droit de voir (moi + membres de mes cercles).
// La RLS garantit qu'on ne récupère QUE des personnes d'un cercle partagé.
export async function getVisibleMembers(): Promise<MemberLoc[]> {
  const [{ data: profiles }, { data: locs }] = await Promise.all([
    supabase.from('profiles').select('id, display_name, phone'),
    supabase.from('locations').select('*'),
  ]);
  const locMap = new Map((locs ?? []).map((l: any) => [l.user_id, l]));
  return (profiles ?? []).map((p: any): MemberLoc => {
    const l: any = locMap.get(p.id);
    return {
      user_id: p.id,
      display_name: p.display_name,
      phone: p.phone ?? null,
      lat: l?.lat ?? null,
      lng: l?.lng ?? null,
      accuracy: l?.accuracy ?? null,
      updated_at: l?.updated_at ?? null,
    };
  });
}

export type MyProfile = { id: string; display_name: string; phone: string | null };

export async function getMyProfile(): Promise<MyProfile | null> {
  const { data: u } = await supabase.auth.getUser();
  const uid = u.user?.id;
  if (!uid) return null;
  const { data } = await supabase
    .from('profiles')
    .select('id, display_name, phone')
    .eq('id', uid)
    .single();
  return (data as MyProfile) ?? null;
}

export async function updateMyProfile(displayName: string, phone: string | null): Promise<void> {
  const { data: u } = await supabase.auth.getUser();
  const uid = u.user?.id;
  if (!uid) return;
  const { error } = await supabase
    .from('profiles')
    .update({ display_name: displayName.trim(), phone: phone?.trim() || null })
    .eq('id', uid);
  if (error) throw error;
}

export async function deleteMyAccount(): Promise<void> {
  const { error } = await supabase.rpc('delete_my_account');
  if (error) throw error;
}

// ---------- SOS ----------
export type SosAlert = {
  id: string;
  user_id: string;
  lat: number | null;
  lng: number | null;
  message: string | null;
  status: string;
  created_at: string;
  display_name?: string;
};

export async function createSOS(
  lat: number | null,
  lng: number | null,
  message?: string,
): Promise<void> {
  const { data: u } = await supabase.auth.getUser();
  const uid = u.user?.id;
  if (!uid) throw new Error('Non connecté');
  const { error } = await supabase
    .from('sos_alerts')
    .insert({ user_id: uid, lat, lng, message: message ?? null });
  if (error) throw error;
}

export async function getActiveSOS(): Promise<SosAlert[]> {
  const { data } = await supabase
    .from('sos_alerts')
    .select('*')
    .eq('status', 'active')
    .order('created_at', { ascending: false });
  const ids = [...new Set((data ?? []).map((s: any) => s.user_id))];
  const names = new Map<string, string>();
  if (ids.length) {
    const { data: p } = await supabase.from('profiles').select('id, display_name').in('id', ids);
    (p ?? []).forEach((x: any) => names.set(x.id, x.display_name));
  }
  return (data ?? []).map((s: any) => ({ ...s, display_name: names.get(s.user_id) }));
}

export async function resolveSOS(id: string): Promise<void> {
  await supabase
    .from('sos_alerts')
    .update({ status: 'resolved', resolved_at: new Date().toISOString() })
    .eq('id', id);
}

// ---------- ALERTE DISPARITION ----------
export type MissingAlert = {
  id: string;
  reporter_id: string;
  person_name: string;
  age: number | null;
  photo_url: string | null;
  last_seen_lat: number | null;
  last_seen_lng: number | null;
  last_seen_place: string | null;
  last_seen_at: string | null;
  description: string | null;
  contact_phone: string | null;
  status: string;
  created_at: string;
};

export type NewMissingAlert = {
  person_name: string;
  age: number | null;
  photo_url: string | null;
  last_seen_lat: number | null;
  last_seen_lng: number | null;
  last_seen_place: string | null;
  last_seen_at: string | null;
  description: string | null;
  contact_phone: string | null;
};

export async function getMissingAlerts(): Promise<MissingAlert[]> {
  const { data, error } = await supabase
    .from('missing_alerts')
    .select('*')
    .eq('status', 'active')
    .order('created_at', { ascending: false });
  if (error) throw error;
  return (data ?? []) as MissingAlert[];
}

export async function createMissingAlert(input: NewMissingAlert): Promise<void> {
  const { data: u } = await supabase.auth.getUser();
  const uid = u.user?.id;
  if (!uid) throw new Error('Non connecté');
  const { error } = await supabase.from('missing_alerts').insert({ reporter_id: uid, ...input });
  if (error) throw error;
}

export async function resolveMissingAlert(id: string): Promise<void> {
  await supabase.from('missing_alerts').update({ status: 'found' }).eq('id', id);
}

export async function isMyAlert(reporterId: string): Promise<boolean> {
  const { data } = await supabase.auth.getUser();
  return data.user?.id === reporterId;
}

// Upload d'une photo (data/blob URI) vers le bucket public 'alerts'. Renvoie l'URL publique.
export async function uploadAlertPhoto(uri: string): Promise<string> {
  const res = await fetch(uri);
  const blob = await res.blob();
  const ext = (blob.type && blob.type.split('/')[1]) || 'jpg';
  const path = `missing/${Date.now()}-${Math.random().toString(36).slice(2, 8)}.${ext}`;
  const { error } = await supabase.storage.from('alerts').upload(path, blob, {
    contentType: blob.type || 'image/jpeg',
    upsert: false,
  });
  if (error) throw error;
  return supabase.storage.from('alerts').getPublicUrl(path).data.publicUrl;
}

export async function upsertMyLocation(
  lat: number,
  lng: number,
  accuracy: number | null,
): Promise<void> {
  const { data } = await supabase.auth.getUser();
  const uid = data.user?.id;
  if (!uid) return;
  const { error } = await supabase.from('locations').upsert({
    user_id: uid,
    lat,
    lng,
    accuracy,
    updated_at: new Date().toISOString(),
  });
  if (error) throw error;
}
