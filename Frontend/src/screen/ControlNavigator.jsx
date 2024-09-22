import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ControlScreen from "./Control";
import HomeScreen from "./Home";
import SmartHomeScreen from "./SmartHome";
import Login from "./Login";
import SignUp from "./SignUp";
import React from "react";
import EmotionScreen from "./Emotion";
import HighlightScreen from "./Highlight";

const ControlStack = createNativeStackNavigator();

export default function ControlNavigator() {
  return (
    <ControlStack.Navigator 
      screenOptions={{
        headerStyle: {
          backgroundColor: 'transparent',
        },
        headerTintColor: '#fff',
        headerTransparent: true,
        headerTitleAlign: 'center',
      }}
    >
        <ControlStack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: '' }}
        />
        <ControlStack.Screen 
          name="Control" 
          component={ControlScreen} 
          options={{ title: 'HEROBOT REMOTE' }}
        />
        <ControlStack.Screen 
          name="SmartHome" 
          component={SmartHomeScreen} 
          options={{ title: '' }}
        />
        <ControlStack.Screen 
          name="Login" 
          component={Login} 
          options={{ title: '로그인' }}
        />
        <ControlStack.Screen 
          name="SignUp" 
          component={SignUp} 
          options={{ title: '회원가입' }}
        />
        <ControlStack.Screen 
          name="Emotion" 
          component={EmotionScreen} 
          options={{ title: '감정 인식' }}
        />
        <ControlStack.Screen 
          name="Highlight" 
          component={HighlightScreen} 
          options={{ title: '하이라이트' }}
        />
    </ControlStack.Navigator>
  );
}
