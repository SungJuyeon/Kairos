import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ControlScreen from "./Control";
import HomeScreen from "./Home";
import React from "react";

const ControlStack = createNativeStackNavigator();

export default function ControlNavigator() {
  return (
    <ControlStack.Navigator 
      screenOptions={{
        headerStyle: {
          backgroundColor: 'transparent', // 배경색을 투명으로 설정
        },
        headerTintColor: '#fff', // 헤더의 텍스트 색상
        headerTransparent: true, // 헤더를 투명하게 설정
      }}
    >
        <ControlStack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />
        <ControlStack.Screen 
          name="Control" 
          component={ControlScreen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />
    </ControlStack.Navigator>
  );
}
