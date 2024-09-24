import React, { useEffect, useState, useContext } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, TextInput, Dimensions, Alert, KeyboardAvoidingView, Platform } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import AsyncStorage from '@react-native-async-storage/async-storage';
import MyPage from "./MyPage";
import { AuthContext } from './AuthContext';

const { width, height } = Dimensions.get('window');

const BASE_URL = 'http://10.0.2.2:8080';

export default function Login() {
    const { navigate } = useNavigation();
    const [id, setId] = useState('');
    const [password, setPassword] = useState('');

    const [idFocused, setIdFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);

    const { isLoggedIn, login, logout } = useContext(AuthContext);

    useEffect(() => {
        const checkLoginStatus = async () => {
            try {
                const token = await AsyncStorage.getItem('token');
                if (token) {
                    login();
                } else {
                    logout();
                }
            } catch (error) {
                console.error('로그인 상태 불러오기 실패', error);
                logout();
            }
        };

        checkLoginStatus();
    }, []);

    const tryLogin = async () => {
        try {
            const response = await fetch(`${BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: id,
                    password,
                }),
            });

            console.log('응답 상태:', response.status);

            if (response.ok) {
                const accessToken = response.headers.get('access');
                if (accessToken) {
                    await AsyncStorage.setItem('token', accessToken);
                    login();
                    Alert.alert('로그인 성공', '환영합니다!');
                } else {
                    Alert.alert('로그인 실패', '토큰을 찾을 수 없습니다.');
                }
            } else {
                const errorText = await response.text();
                console.log('로그인 실패 내용:', errorText);
                Alert.alert('로그인 실패', errorText);
            }
        } catch (error) {
            console.error('오류 발생:', error);
            Alert.alert('오류 발생', '다시 시도해 주세요.');
        }
    };

    return (
        <KeyboardAvoidingView
            style={{ flex: 1 }} // 전체 화면을 차지하도록 설정
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'} // iOS와 Android에 따라 다르게 설정
            keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0} // 필요에 따라 조정
        >
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
                            placeholder="ID"
                            onFocus={() => setIdFocused(true)}
                            onBlur={() => setIdFocused(false)}
                            focused={idFocused}
                        />
                        <StyledTextInput
                            onChangeText={setPassword}
                            value={password}
                            placeholderTextColor="gray"
                            placeholder="PASSWORD"
                            secureTextEntry={true}
                            onFocus={() => setPasswordFocused(true)}
                            onBlur={() => setPasswordFocused(false)}
                            focused={passwordFocused}
                        />
                        <RowContainer>
                            <LoginButton onPress={tryLogin}>
                                <ButtonText>로그인</ButtonText>
                            </LoginButton>
                            <Button onPress={() => navigate('FindUserData')}>
                                <ButtonText>내 정보 찾기</ButtonText>
                            </Button>
                        </RowContainer>
                        <StyledText>처음이시라면...?</StyledText>
                        <SignIn onPress={() => navigate('SignUp')}>
                            <ButtonText>회원 가입 하러가기</ButtonText>
                        </SignIn>
                    </View>
                )}
            </Container>
        </KeyboardAvoidingView>
    );
}

const StyledText = styled.Text`
    color: #FFFFFF;
    font-size: ${height * 0.025}px;
    margin-top: ${height * 0.07}px;
    margin-bottom: 5px;
    margin-left: 10px;
    font-weight: bold;
`;

const StyledTextInput = styled.TextInput`
    height: ${height * 0.06}px;
    width: ${width * 0.5}px;
    border-color: ${({ focused }) => (focused ? '#FFB0F9' : 'white')};
    border-bottom-width: 3px;
    padding: 10px;
    margin: 10px 0;
    color: white;
    font-size: ${height * 0.022}px;
    background-color: #222222;
`;

const Title = styled.Text`
    color: #FFFFFF;
    font-size: ${height * 0.065}px;
    margin-bottom: ${height * 0.05}px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
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

const LoginButton = styled.TouchableOpacity`
    background-color: #FFCEFF;
    padding: ${height * 0.02}px ${width * 0.06}px;
    border-radius: 10px;
    margin: 0 10px;
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
