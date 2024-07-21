import { createNativeStackNavigator } from "@react-navigation/native-stack";
import HomeScreen from "./Home";
import SearchScreen from "./Screen2";
import StoreScreen from "./Screen3";
import DensityScreen from "./Density";
import React from "react";

const HomeStack = createNativeStackNavigator();

export default function HomeStackNavigator() {
  return (
    <HomeStack.Navigator screenOptions={{ headerShown: false }}>
        <HomeStack.Screen name="Density" component={DensityScreen} />
        <HomeStack.Screen name="Home" component={HomeScreen} />
        <HomeStack.Screen name="Search" component={SearchScreen} />
        <HomeStack.Screen name="Store" component={StoreScreen} />
    </HomeStack.Navigator>
  );
}