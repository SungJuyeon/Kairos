import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import ControlNavigator from "./src/screen/ControlNavigator";
import MyPageNavigator from "./src/screen/MyPageNavigator";
import ChatNavigator from "./src/screen/ChatNavigator";
import HighlightNavigator from "./src/screen/HighlightNavigator";
import { StatusBar } from 'react-native';
import React from "react";
import { AuthProvider } from './src/screen/AuthContext';
import { Ionicons } from '@expo/vector-icons';

const BottomTab = createBottomTabNavigator();

const URI = '172.30.1.68';

export default function App() {
  return (
    <AuthProvider>
    <StatusBar
      barStyle="light-content"
    />
    <NavigationContainer>
      <BottomTab.Navigator
                screenOptions={({ route }) => ({
                  headerShown: false,
                  tabBarStyle: {
                    backgroundColor: '#222222',
                    activeTintColor: '#FFFFFF',
                    inactiveTintColor: 'gray'
                  },
                  tabBarIcon: ({ color, size, focused }) => {
                    let iconName;
                    const iconColor = '#FFFFFF'

                    if (route.name === 'Control') {
                      iconName = focused ? 'camera' : 'camera-outline';
                    } else if (route.name === 'MyPage') {
                      iconName = focused ? 'person' : 'person-outline';
                    } else if (route.name === 'Chat') {
                      iconName = focused ? 'chatbox' : 'chatbox-outline';
                    } else if (route.name === 'Highlight') {
                      iconName = focused ? 'star' : 'star-outline';
                    }
                    return <Ionicons name={iconName} size={size} color={iconColor} />;
                  },
                  tabBarLabel: () => null, // 탭 바 텍스트를 숨깁니다.
                })}>
        <BottomTab.Screen name="Control" component={ControlNavigator} />
        <BottomTab.Screen name="Chat" component={ChatNavigator} />
        <BottomTab.Screen name="Highlight" component={HighlightNavigator} />
        <BottomTab.Screen name="MyPage" component={MyPageNavigator} />
      </BottomTab.Navigator>
    </NavigationContainer>
    </AuthProvider>
  );
}