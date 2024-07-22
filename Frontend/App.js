import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import HomeStackNavigator from "./src/screen/HomeStackNavigator";
import MyPageStackNavigator from "./src/screen/MyPageNavigator";
import MyScheduleNavigator from "./src/screen/MyScheduleNavigator";
import { StatusBar } from 'react-native';
import React from "react";
import { AuthProvider } from './src/screen/AuthContext';
import { Ionicons } from '@expo/vector-icons';

const BottomTab = createBottomTabNavigator();

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
                    backgroundColor: 'black',
                    activeTintColor: 'white',
                    inactiveTintColor: 'gray'
                  },
                  tabBarIcon: ({ color, size, focused }) => {
                    let iconName;
                    const iconColor = 'white'
              
                    if (route.name === 'Home') {
                      iconName = focused ? 'home' : 'home-outline';
                    } else if (route.name === 'MyPage') {
                      iconName = focused ? 'person' : 'person-outline';
                    } else if (route.name === 'MySchedule') {
                      iconName = focused ? 'calendar-clear' : 'calendar-clear-outline';
                    }
                    return <Ionicons name={iconName} size={size} color={iconColor} />;
                  },
                  tabBarLabel: () => null, // 탭 바 텍스트를 숨깁니다.
                })}>
        <BottomTab.Screen name="Home" component={HomeStackNavigator} />
        <BottomTab.Screen name="MySchedule" component={MyScheduleNavigator} />
        <BottomTab.Screen name="MyPage" component={MyPageStackNavigator} />
      </BottomTab.Navigator>
    </NavigationContainer>
    </AuthProvider>
  );
}