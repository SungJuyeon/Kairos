import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ChatScreen from "./Chat";
import VoiceChatScreen from "./VoiceChat"
import React from "react";

const ChatStack = createNativeStackNavigator();

export default function ChatNavigator() {
  return (
    <ChatStack.Navigator screenOptions={{ headerShown: false }}>
        <ChatStack.Screen name="Chat" component={ChatScreen} />
        <ChatStack.Screen name="VoiceChat" component={VoiceChatScreen} />
    </ChatStack.Navigator>
  );
}