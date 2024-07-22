import { createNativeStackNavigator } from "@react-navigation/native-stack";
import MyScheduleScreen from "./MySchedule";
import InputMyScheduleScreen from "./InputMySchedule";
import React from "react";

const MyScheduleStack = createNativeStackNavigator();

export default function MyScheduleNavigator() {
  return (
    <MyScheduleStack.Navigator screenOptions={{ headerShown: false }}>
        <MyScheduleStack.Screen name="MySchedule" component={MyScheduleScreen} />
        <MyScheduleStack.Screen name="InputMySchedule" component={InputMyScheduleScreen} />
    </MyScheduleStack.Navigator>
  );
}