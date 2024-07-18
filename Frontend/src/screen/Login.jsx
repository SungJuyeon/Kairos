import React, { useEffect, useState, useContext } from "react";
import axios from 'axios';
import { View, Text, SafeAreaView, TouchableOpacity, TextInput } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import AsyncStorage from '@react-native-async-storage/async-storage';
import MyPage from "./MyPage";
import { AuthContext } from './AuthContext';


export default function Login() {
    const { navigate } = useNavigation();
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');

    // TextInput이 포커싱 되었을 때 색상 변경
    const [idFocused, setIdFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);

    // 로그인 관련
    const { isLoggedIn, login, logout } = useContext(AuthContext);
    
    // 앱 실행 시 로그인 상태에 따라 화면 다르게 출력
    useEffect(() => {
        const checkLoginStatus = async () => {
          try {
            // AsyncStorage에서 사용자 정보 가져오기
            const userInfo = await AsyncStorage.getItem('userInfo');
            if (userInfo) {
              // 사용자 정보가 있다면 로그인 상태로 설정
              login();
            } else {
              // 사용자 정보가 없다면 로그아웃 상태로 설정
              logout();
            }
          } catch (error) {
            console.error('로그인 상태 불러오기 실패', error);
          }
        };
    
        checkLoginStatus();
      }, []);
    
    // 로그인 버튼 클릭 시
    const tryLogin = async () => {
        try {
            const userData = { loginId: id, pw: password }
            const response = await axios.post('http://localhost:8080/login', userData, {
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                // 로그인 성공 처리
                const onLoginSuccess = async (userData) => {
                    try {
                        // 사용자 정보를 AsyncStorage에 저장
                        await AsyncStorage.setItem('userInfo', JSON.stringify(userData));
                        // 로그인 상태 변경
                        login();
                    } catch (error) {
                      console.error('로그인 정보 저장 실패', error);
                    }
                  };
                console.log(response.data);
            });
        // 로그인 실패
        } catch (error) {
          console.error('로그인이 실패했습니다.', error);
        }
      };

    return (
        <Container>
        {isLoggedIn ? (
          // 로그인 성공 시 보여줄 화면
          <MyPage />
        ) : (
          // 로그인 실패 시 보여줄 화면
          <View>
            <Title>Log In!</Title>
            <StyledTextInput
              onChangeText={(text) => setId(text)}
              value={id}
              placeholderTextColor="gray"
              placeholder="아이디"
              onFocus={() => setIdFocused(true)}
              onBlur={() => setIdFocused(false)}
              focused={idFocused}
            />
            <StyledTextInput
              onChangeText={(text) => setPassword(text)}
              value={password}
              placeholderTextColor="gray"
              placeholder="비밀번호"
              secureTextEntry={true}
              onFocus={() => setPasswordFocused(true)}
              onBlur={() => setPasswordFocused(false)}
              focused={passwordFocused}
            />
            <RowContainer>
              {/* <Button onPress={tryLogin}>
                <ButtonText>로그인</ButtonText>
              </Button> */}
              <Button onPress={() => login()}>
                <ButtonText>로그인</ButtonText>
              </Button>
              <Button onPress={() => navigate('FindUserData')}>
                <ButtonText>내 정보 찾기</ButtonText>
              </Button>
            </RowContainer>
            <StyledText>처음이시라면...?</StyledText>
        <SignIn onPress={() => navigate('SignIn')}>
          <ButtonText>회원 가입 하러가기</ButtonText>
        </SignIn>
          </View>
        )}
      </Container>
    );
}

const StyledText = styled.Text`
    color: white;
    font-size: 15px;
    margin-top: 70px;
    margin-bottom: 5px;
    margin-left: 10px;
    font-weight: bold;
`;

const StyledTextInput = styled.TextInput`
    height: 50px;
    width: 80%px;
    border-color: ${({ focused }) => (focused ? '#0CDAE0' : 'white')};
    border-bottom-width: 3px;
    padding: 10px;
    margin: 10px 0;
    color: white;
    font-size: 18px;
    background-color: #000000;
`;

const Title = styled.Text`
    color: white;
    font-size: 50px;
    margin-bottom: 40px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #000000;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const RowContainer = styled.View`
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 0 10px;
`;

const ButtonText = styled.Text`
  color: black;
  font-size: 18px;
  font-weight: bold;
`;

const SignIn = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 5px;
`;