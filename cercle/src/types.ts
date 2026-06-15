export type CerclesStackParamList = {
  CerclesList: undefined;
  CircleDetail: { circleId: string; name: string; inviteCode: string };
};

export type AlertsStackParamList = {
  AlertsList: undefined;
  ReportMissing: undefined;
};

export type ProfileStackParamList = {
  ProfileMain: undefined;
  Privacy: undefined;
};

export type TabParamList = {
  Carte: undefined;
  Cercles: undefined;
  Alertes: undefined;
  Profil: undefined;
};

export type Circle = {
  id: string;
  name: string;
  owner: string;
  invite_code: string;
  created_at?: string;
};

export type MemberLoc = {
  user_id: string;
  display_name: string;
  phone: string | null;
  lat: number | null;
  lng: number | null;
  accuracy: number | null;
  updated_at: string | null;
};
