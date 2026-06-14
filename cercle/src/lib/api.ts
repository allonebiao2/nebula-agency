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
