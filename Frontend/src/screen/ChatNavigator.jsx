import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ChatScreen from "./Chat";
import VoiceChatScreen from "./VoiceChat"
import React from "react";

const ChatStack = createNativeStackNavigator();

export default function ChatNavigator() {
  return (
    <ChatStack.Navigator
      screenOptions={{
        headerStyle: {
          backgroundColor: 'transparent', // 배경색을 투명으로 설정
        },
        headerTintColor: '#fff', // 헤더의 텍스트 색상
        headerTransparent: true, // 헤더를 투명하게 설정
        headerTitleAlign: 'center', // 타이틀 정렬을 가운데로 설정
    }}
    >
        <ChatStack.Screen name="VoiceChat" component={VoiceChatScreen} />
        <ChatStack.Screen name="Chat" component={ChatScreen} />
    </ChatStack.Navigator>
  );
}