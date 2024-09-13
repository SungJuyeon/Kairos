import { createNativeStackNavigator } from "@react-navigation/native-stack";
import HighlightScreen from "./Highlight";
import EmotionScreen from "./Emotion";
import RepositoryScreen from "./Repository";
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
      headerTitleAlign: 'center', // 타이틀 정렬을 가운데로 설정
    }}
    >

        <HighlightStack.Screen 
          name="Emotion" 
          component={EmotionScreen} 
          options={{ title: "Today's Highlight" }} // 타이틀을 직접 설정
        />

        <HighlightStack.Screen 
          name="Repository" 
          component={RepositoryScreen} 
          options={{ title: "" }} // 타이틀을 직접 설정
        />

    </HighlightStack.Navigator>
  );
}
