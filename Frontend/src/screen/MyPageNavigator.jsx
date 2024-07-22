import { createNativeStackNavigator } from "@react-navigation/native-stack";
import MyPageScreen from "./MyPage";
import LoginScreen from "./Login";
import SignInScreen from "./SignIn";
import FindUserDataScreen from "./FindUserData";
import FindIdScreen from "./FindId";
import FindPasswordScreen from "./FindPassword";
import React from "react";

const MyPageStack = createNativeStackNavigator();

export default function MyPageStackNavigator() {
  return (
    <MyPageStack.Navigator screenOptions={{ headerShown: false }}>
        <MyPageStack.Screen name="Login" component={LoginScreen} />
        <MyPageStack.Screen name="SignIn" component={SignInScreen} />
        <MyPageStack.Screen name="MyPage" component={MyPageScreen} />
        <MyPageStack.Screen name="FindUserData" component={FindUserDataScreen} />
        <MyPageStack.Screen name="FindId" component={FindIdScreen} />
        <MyPageStack.Screen name="FindPassword" component={FindPasswordScreen} />
    </MyPageStack.Navigator>
  );
}