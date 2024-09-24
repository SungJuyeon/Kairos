import React, { useState } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Alert } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://10.0.2.2:8080';

export default function SignIn() {
    const { navigate } = useNavigation();

    const [password, setPassword] = useState('');
    const [conformPW, setConformPW] = useState('');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [nickname, setNickname] = useState('');

    const [senderUsername, setSenderUsername] = useState('');
    const [receiverUsername, setReceiverUsername] = useState('');

    // TextInput이 포커싱 되었을 때 색상 변경
    const [usernameFocused, setUsernameFocused] = useState(false);
    const [idFocused, setIdFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);
    const [conformPWFocused, setConformPWFocused] = useState(false);
    const [emailFocused, setEmailFocused] = useState(false);
    const [nicknameFocused, setNicknameFocused] = useState(false);


    const inviteFamily = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');
    
            // senderUsername 받아오기
            const usernameResponse = await fetch(`${BASE_URL}/user/username`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });
    

            if (!usernameResponse.ok) {
                throw new Error('네트워크 응답이 좋지 않습니다.');
            }
    
            const senderUsername = await usernameResponse.text(); // 또는 await usernameResponse.json() - 응답 형식에 따라
            setSenderUsername(senderUsername);
            
            // receiverUsername 설정
            const receiverUsername = username; // 현재 입력된 username 사용
    
            // POST 요청
            const requestResponse = await fetch(`${BASE_URL}/family/request`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    senderUsername,
                    receiverUsername,
                }),
            });
    
            if (!requestResponse.ok) {
                throw new Error('네트워크 응답이 좋지 않습니다.');
            }
    
            const data = await requestResponse.json();
            console.log(data);

            // 요청이 성공적으로 완료되면 알림창 띄우기
            Alert.alert('성공', '가족 요청이 완료되었습니다.');


        } catch (error) {
            Alert.alert('오류 발생', error.message);
        }
    };

    return (
        <Container>
            <Title>가족 초대</Title>
            <InputContainer>
                <Text style={{ color: 'white', fontWeight: 'bold' }}>유저 ID</Text>
                <StyledTextInput
                    onChangeText={text => setUsername(text)}
                    value={username}
                    onFocus={() => setUsernameFocused(true)}
                    onBlur={() => setUsernameFocused(false)}
                    focused={usernameFocused}
                />
            </InputContainer>
            <RowContainer>
                <Button2 onPress={inviteFamily}>
                    <ButtonText>초대하기</ButtonText>
                </Button2>
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
    background-color: #222222;
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
    margin: 10 10px;
`;

const Button2 = styled.TouchableOpacity`
    background-color: #FFCEFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 10px;
`;

const Button3 = styled.TouchableOpacity`
    background-color: #ADCDFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 10px;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 10px;
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
    background-color: #222222;
`;

const RowContainer = styled.View`
    flex-direction: row;
    justify-content: left;
    align-items: left;
    margin-top: 30px;
    margin-left: 20px;
`;
