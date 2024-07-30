import React, { useEffect, useState, useContext } from "react";
import axios from 'axios';
import { View, Text, SafeAreaView, TouchableOpacity, TextInput, Dimensions, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import AsyncStorage from '@react-native-async-storage/async-storage';
import MyPage from "./MyPage";
import { AuthContext } from './AuthContext';

const { width, height } = Dimensions.get('window');

export default function Login() {
    const { navigate } = useNavigation();
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');

    const [idFocused, setIdFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);

    // 백엔드에서는 id 말고 username을 사용하기에
    const [username, setUsername] = useState('');

    const { isLoggedIn, login, logout } = useContext(AuthContext);
    
    useEffect(() => {
        const checkLoginStatus = async () => {
          try {
            const userInfo = await AsyncStorage.getItem('userInfo');
            if (userInfo) {
              login();
            } else {
              logout();
            }
          } catch (error) {
            console.error('로그인 상태 불러오기 실패', error);
          }
        };
    
        checkLoginStatus();
      }, []);
    

    // 로그인 버튼 클릭시 실행
    const tryLogin = async () => {
        setUsername(id);

        try {
            const response = await fetch('http://localhost:8080/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    password,
                }),
            });
            
            const data = await response.text();
            if (response.ok) {
                login();
                Alert.alert('로그인 성공', data);
            } else {
                console.log(data);
                Alert.alert('로그인 실패', data);
            }
        } catch (error) {
            console.error(error);
            Alert.alert('오류 발생', '다시 시도해 주세요.');
        }
    };

    return (
        <Container>
            {isLoggedIn ? (
                <MyPage />
            ) : (
                <View style={{ alignItems: 'center' }}>
                    <Title>Log In!</Title>
                    <StyledTextInput
                        onChangeText={setId}
                        value={id}
                        placeholderTextColor="gray"
                        placeholder="이름"
                        onFocus={() => setIdFocused(true)}
                        onBlur={() => setIdFocused(false)}
                        focused={idFocused}
                    />
                    <StyledTextInput
                        onChangeText={setPassword}
                        value={password}
                        placeholderTextColor="gray"
                        placeholder="비밀번호"
                        secureTextEntry={true}
                        onFocus={() => setPasswordFocused(true)}
                        onBlur={() => setPasswordFocused(false)}
                        focused={passwordFocused}
                    />
                    <RowContainer>
                        <Button onPress={tryLogin}>
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
    font-size: ${height * 0.025}px;
    margin-top: ${height * 0.07}px;
    margin-bottom: 5px;
    margin-left: 10px;
    font-weight: bold;
`;

const StyledTextInput = styled.TextInput`
    height: ${height * 0.06}px;
    width: ${width * 0.65}px;
    border-color: ${({ focused }) => (focused ? '#0CDAE0' : 'white')};
    border-bottom-width: 3px;
    padding: 10px;
    margin: 10px 0;
    color: white;
    font-size: ${height * 0.022}px;
    background-color: #000000;
`;

const Title = styled.Text`
    color: white;
    font-size: ${height * 0.065}px;
    margin-bottom: ${height * 0.05}px;
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
    margin-top: ${height * 0.02}px;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: ${height * 0.02}px ${width * 0.06}px;
    border-radius: 10px;
    margin: 0 10px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: ${height * 0.022}px;
    font-weight: bold;
`;

const SignIn = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: ${height * 0.02}px ${width * 0.06}px;
    border-radius: 10px;
    margin: 5px;
`;
