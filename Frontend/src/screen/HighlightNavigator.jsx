import { createNativeStackNavigator } from "@react-navigation/native-stack";
import HighlightScreen from "./Highlight";
import React from "react";

const HighlightStack = createNativeStackNavigator();

export default function HighlightNavigator() {
  return (
    <HighlightStack.Navigator 
      screenOptions={{
        headerStyle: {
          backgroundColor: 'transparent', // 배경색을 투명으로 설정
        },
        headerTintColor: '#fff', // 헤더의 텍스트 색상
        headerTransparent: true, // 헤더를 투명하게 설정
      }}
    >
        <HighlightStack.Screen 
          name="Highlight" 
          component={HighlightScreen} 
          options={{ title: '' }} // 타이틀을 직접 설정
        />

    </HighlightStack.Navigator>
  );
}
