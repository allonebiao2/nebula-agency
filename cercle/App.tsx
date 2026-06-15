import 'react-native-url-polyfill/auto';
import React from 'react';
import { ActivityIndicator, StatusBar, View } from 'react-native';
import { NavigationContainer, DefaultTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { AuthProvider, useAuth } from './src/context/AuthContext';
import AuthScreen from './src/screens/AuthScreen';
import HomeScreen from './src/screens/HomeScreen';
import CircleScreen from './src/screens/CircleScreen';
import MapScreen from './src/screens/MapScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import PrivacyScreen from './src/screens/PrivacyScreen';
import AlertsScreen from './src/screens/AlertsScreen';
import ReportMissingScreen from './src/screens/ReportMissingScreen';
import type {
  CerclesStackParamList,
  AlertsStackParamList,
  ProfileStackParamList,
  TabParamList,
} from './src/types';
import { COLORS } from './src/lib/config';

const Tab = createBottomTabNavigator<TabParamList>();
const CerclesStack = createNativeStackNavigator<CerclesStackParamList>();
const AlertsStack = createNativeStackNavigator<AlertsStackParamList>();
const ProfileStack = createNativeStackNavigator<ProfileStackParamList>();

const theme = {
  ...DefaultTheme,
  colors: { ...DefaultTheme.colors, background: COLORS.bg, card: COLORS.bg, text: COLORS.text },
};

const stackOptions = {
  headerStyle: { backgroundColor: COLORS.bg },
  headerTintColor: COLORS.text,
  headerShadowVisible: false,
};

function CerclesNavigator() {
  return (
    <CerclesStack.Navigator screenOptions={stackOptions}>
      <CerclesStack.Screen name="CerclesList" component={HomeScreen} options={{ title: 'Mes cercles' }} />
      <CerclesStack.Screen name="CircleDetail" component={CircleScreen} options={{ title: 'Cercle' }} />
    </CerclesStack.Navigator>
  );
}

function AlertsNavigator() {
  return (
    <AlertsStack.Navigator screenOptions={stackOptions}>
      <AlertsStack.Screen name="AlertsList" component={AlertsScreen} options={{ title: 'Alertes Disparition' }} />
      <AlertsStack.Screen name="ReportMissing" component={ReportMissingScreen} options={{ title: 'Signaler une disparition' }} />
    </AlertsStack.Navigator>
  );
}

function ProfileNavigator() {
  return (
    <ProfileStack.Navigator screenOptions={stackOptions}>
      <ProfileStack.Screen name="ProfileMain" component={ProfileScreen} options={{ title: 'Profil' }} />
      <ProfileStack.Screen name="Privacy" component={PrivacyScreen} options={{ title: 'Confidentialité' }} />
    </ProfileStack.Navigator>
  );
}

function Tabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: COLORS.accent,
        tabBarInactiveTintColor: COLORS.muted,
        tabBarStyle: { backgroundColor: COLORS.card, borderTopColor: COLORS.border },
        tabBarIcon: ({ color, size }) => {
          const icon =
            route.name === 'Carte'
              ? 'map'
              : route.name === 'Cercles'
                ? 'people'
                : route.name === 'Alertes'
                  ? 'alert-circle'
                  : 'person-circle';
          return <Ionicons name={icon as any} size={size} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Carte" component={MapScreen} />
      <Tab.Screen name="Cercles" component={CerclesNavigator} />
      <Tab.Screen name="Alertes" component={AlertsNavigator} />
      <Tab.Screen name="Profil" component={ProfileNavigator} />
    </Tab.Navigator>
  );
}

function Root() {
  const { session, loading } = useAuth();
  if (loading) {
    return (
      <View style={{ flex: 1, backgroundColor: COLORS.bg, justifyContent: 'center' }}>
        <ActivityIndicator color={COLORS.accent} size="large" />
      </View>
    );
  }
  return (
    <NavigationContainer theme={theme}>
      {session ? <Tabs /> : <AuthScreen />}
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <SafeAreaProvider>
      <StatusBar barStyle="light-content" />
      <AuthProvider>
        <Root />
      </AuthProvider>
    </SafeAreaProvider>
  );
}
