import { createNativeStackNavigator } from "@react-navigation/native-stack";
import MyScheduleScreen from "./MySchedule";
import InputMyScheduleScreen from "./InputMySchedule";
import ChatScreen from "./Chat";
import VoiceChatScreen from "./VoiceChat"
import React from "react";

const MyScheduleStack = createNativeStackNavigator();

export default function MyScheduleNavigator() {
  return (
    <MyScheduleStack.Navigator screenOptions={{ headerShown: false }}>
        <MyScheduleStack.Screen name="Chat" component={ChatScreen} />
        <MyScheduleStack.Screen name="VoiceChat" component={VoiceChatScreen} />
        <MyScheduleStack.Screen name="MySchedule" component={MyScheduleScreen} />
        <MyScheduleStack.Screen name="InputMySchedule" component={InputMyScheduleScreen} />
    </MyScheduleStack.Navigator>
  );
}