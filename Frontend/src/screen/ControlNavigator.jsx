import { createNativeStackNavigator } from "@react-navigation/native-stack";
import ControlScreen from "./Control";
import React from "react";

const ControlStack = createNativeStackNavigator();

export default function ControlNavigator() {
  return (
    <ControlStack.Navigator screenOptions={{ headerShown: false }}>
        <ControlStack.Screen name="Control" component={ControlScreen} />
    </ControlStack.Navigator>
  );
}