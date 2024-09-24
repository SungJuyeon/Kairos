import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ControlScreen from "./Control";
import HomeScreen from "./Home";
import SmartHomeScreen from "./SmartHome";
import TutorialScreen from "./Tutorial";
import Function1Screen from "./Function1";
import Function2Screen from "./Function2";
import Function3Screen from "./Function3";
import Function4Screen from "./Function4";
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
        headerTitleAlign: 'center', // 타이틀 정렬을 가운데로 설정
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
          options={{ title: 'HEROBOT REMOTE' }} // 타이틀을 직접 설정
        />
        <ControlStack.Screen 
          name="SmartHome" 
          component={SmartHomeScreen} 
          options={{ title: 'SMARTHOME REMOTE' }} // 타이틀을 직접 설정
        />
        <ControlStack.Screen 
          name="Tutorial" 
          component={TutorialScreen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />
        <ControlStack.Screen 
          name="Function1" 
          component={Function1Screen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />
        <ControlStack.Screen 
          name="Function2" 
          component={Function2Screen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />
        <ControlStack.Screen 
          name="Function3" 
          component={Function3Screen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />
        <ControlStack.Screen 
          name="Function4" 
          component={Function4Screen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />
    </ControlStack.Navigator>
  );
}
