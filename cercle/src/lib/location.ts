import * as Location from 'expo-location';
import { upsertMyLocation } from './api';

// VAGUE 1 : partage de position en AVANT-PLAN uniquement (testable dans Expo Go).
// VAGUE 2 : passage en arrière-plan + notification permanente (build EAS).
let sub: Location.LocationSubscription | null = null;

export async function startSharing(): Promise<boolean> {
  const { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') return false;

  const pos = await Location.getCurrentPositionAsync({
    accuracy: Location.Accuracy.Balanced,
  });
  await upsertMyLocation(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy ?? null);

  sub = await Location.watchPositionAsync(
    { accuracy: Location.Accuracy.Balanced, timeInterval: 15000, distanceInterval: 25 },
    (p) => {
      upsertMyLocation(p.coords.latitude, p.coords.longitude, p.coords.accuracy ?? null).catch(
        () => {},
      );
    },
  );
  return true;
}

export function stopSharing(): void {
  sub?.remove();
  sub = null;
}

export function isSharing(): boolean {
  return sub !== null;
}
