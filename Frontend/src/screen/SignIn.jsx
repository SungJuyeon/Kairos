import React, { useState } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Alert } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import axios from 'axios';

export default function SignIn() {
    const { navigate } = useNavigation();

    const [member, setMember] = useState([]);

    const [id, setId] = useState('');
    const [password, setPassword] = useState('');
    const [conformPW, setConformPW] = useState('');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');

    // TextInput이 포커싱 되었을 때 색상 변경
    const [usernameFocused, setUsernameFocused] = useState(false);
    const [idFocused, setIdFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);
    const [conformPWFocused, setConformPWFocused] = useState(false);
    const [emailFocused, setEmailFocused] = useState(false);

    // 회원가입 버튼 클릭 시
    const createMember = async () => {
        try {
            const response = await fetch('http://localhost:8080/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username,
                    password,
                    email,
                }),
            });

            const data = await response.text();
            if (response.ok) {
                Alert.alert('회원가입 성공', data);
            } else {
                Alert.alert('회원가입 실패', data);
            }
        } catch (error) {
            console.error(error);
            Alert.alert('오류 발생', '다시 시도해 주세요.');
        }
      };

    return (
        <Container>
            <Title>회원가입</Title>
            <InputContainer>
                <Text style={{ color: 'white', fontWeight: 'bold' }}>이름</Text>
                <StyledTextInput
                    onChangeText={text => setUsername(text)}
                    value={username}
                    onFocus={() => setUsernameFocused(true)}
                    onBlur={() => setUsernameFocused(false)}
                    focused={usernameFocused}
                    //placeholder="이름"
                />
                <Text style={{ color: 'white', fontWeight: 'bold' }}>아이디</Text>
                <StyledTextInput
                    onChangeText={text => setId(text)}
                    value={id}
                    onFocus={() => setIdFocused(true)}
                    onBlur={() => setIdFocused(false)}
                    focused={idFocused}
                    //placeholder="아이디"
                />
                <Text style={{ color: 'white', fontWeight: 'bold' }}>비밀번호</Text>
                <StyledTextInput
                    onChangeText={text => setPassword(text)}
                    value={password}
                    secureTextEntry={true}
                    onFocus={() => setPasswordFocused(true)}
                    onBlur={() => setPasswordFocused(false)}
                    focused={passwordFocused}
                    //placeholder="비밀번호"
                />
                <Text style={{ color: 'white', fontWeight: 'bold' }}>비밀번호 확인</Text>
                <StyledTextInput
                    onChangeText={text => setConformPW(text)}
                    value={conformPW}
                    secureTextEntry={true}
                    onFocus={() => setConformPWFocused(true)}
                    onBlur={() => setConformPWFocused(false)}
                    focused={conformPWFocused}
                    //placeholder="비밀번호 확인"
                />
                <Text style={{ color: 'white', fontWeight: 'bold' }}>E-mail</Text>
                <StyledTextInput
                    onChangeText={text => setEmail(text)}
                    value={email}
                    keyboardType="email-address"
                    autoCapitalize="none"
                    autoCorrect={false}
                    onFocus={() => setEmailFocused(true)}
                    onBlur={() => setEmailFocused(false)}
                    focused={emailFocused}
                    //placeholder="이메일"
                />
            </InputContainer>
            <RowContainer>
                <Button onPress={createMember}>
                    <ButtonText>회원 가입</ButtonText>
                </Button>
                <BackButton onPress={() => navigate("Login")}>
                    <ButtonText>뒤로 가기</ButtonText>
                </BackButton>
            </RowContainer>
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 40px;
    margin-right: 125px;
    margin-bottom: 50px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #000000;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const InputContainer = styled.View`
    width: 100%;
    padding: 0 20px;
    margin-left: 25%;
`;

const BackButton = styled.TouchableOpacity`
    background-color: #AAAAAA;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 0 10px;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 0 10px;
`;

const ButtonText = styled.Text`
  color: black;
  font-size: 16px;
  font-weight: bold;
`;

const StyledTextInput = styled.TextInput`
    height: 40px;
    width: 70%;
    border-color: ${({ focused }) => (focused ? '#0CDAE0' : 'white')};
    border-bottom-width: 2px;
    padding: 10px;
    margin-top: 5px;
    margin-bottom: 15px;
    color: white;
    font-size: 18px;
    background-color: #000000;
`;

const RowContainer = styled.View`
    flex-direction: row;
    justify-content: left;
    align-items: left;
    margin-top: 30px;
    margin-left: 20px;
`;
