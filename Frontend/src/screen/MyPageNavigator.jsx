import { createNativeStackNavigator } from "@react-navigation/native-stack";
import MyPageScreen from "./MyPage";
import LoginScreen from "./Login";
import SignUpScreen from "./SignUp";
import FindUserDataScreen from "./FindUserData";
import FindIdScreen from "./FindId";
import FindPasswordScreen from "./FindPassword";
import ScheduleManageScreen from "./ScheduleManage";
import FamilyManageScreen from "./FamilyManage";
import FamilyAddScreen from "./FamilyAdd";
import React from "react";

const MyPageStack = createNativeStackNavigator();

export default function MyPageNavigator() {
  return (
    <MyPageStack.Navigator screenOptions={{
      headerStyle: {
        backgroundColor: 'transparent', // 배경색을 투명으로 설정
      },
      headerTintColor: '#fff', // 헤더의 텍스트 색상
      headerTransparent: true, // 헤더를 투명하게 설정
    }}>
        <MyPageStack.Screen name="Login" component={LoginScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="SignUp" component={SignUpScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="MyPage" component={MyPageScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="FindUserData" component={FindUserDataScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="FindId" component={FindIdScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="FindPassword" component={FindPasswordScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="ScheduleManage" component={ScheduleManageScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="FamilyManage" component={FamilyManageScreen} options={{ title: '' }} />
        <MyPageStack.Screen name="FamilyAdd" component={FamilyAddScreen} options={{ title: '' }} />
    </MyPageStack.Navigator>
  );
}