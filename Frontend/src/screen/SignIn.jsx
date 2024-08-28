import React, { useState } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Alert } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import axios from 'axios';
// import DocumentPicker from 'react-native-document-picker';

export default function SignIn() {
    const { navigate } = useNavigation();

    const [password, setPassword] = useState('');
    const [conformPW, setConformPW] = useState('');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [nickname, setNickname] = useState('');

    // TextInput이 포커싱 되었을 때 색상 변경
    const [usernameFocused, setUsernameFocused] = useState(false);
    const [idFocused, setIdFocused] = useState(false);
    const [passwordFocused, setPasswordFocused] = useState(false);
    const [conformPWFocused, setConformPWFocused] = useState(false);
    const [emailFocused, setEmailFocused] = useState(false);
    const [nicknameFocused, setNicknameFocused] = useState(false);

    // 회원가입 버튼 클릭 시
    const createMember = async () => {

        // 비밀번호 입력과 비밀번호 확인입력 비교
        if (password != conformPW) {
            Alert.alert('비밀번호가 일치하지 않습니다.')
            return;
        }


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
                    nickname,
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

      // 파일 업로드를 위한 코드
    //   const uploadFile = async () => {
    //     try {
    //       const res = await DocumentPicker.pick({
    //         type: [DocumentPicker.types.allFiles],
    //       });
    
    //       // 여기에서 파일을 서버로 업로드하는 로직 추가
    //       console.log('파일 선택됨: ', res.uri);
    //     } catch (err) {
    //       if (DocumentPicker.isCancel(err)) {
    //         console.log('사용자에 의해 취소됨');
    //       } else {
    //         throw err;
    //       }
    //     }
    //   };

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
                <Text style={{ color: 'white', fontWeight: 'bold' }}>닉네임</Text>
                <StyledTextInput
                    onChangeText={text => setNickname(text)}
                    value={nickname}
                    onFocus={() => setNicknameFocused(true)}
                    onBlur={() => setNicknameFocused(false)}
                    focused={nicknameFocused}
                    //placeholder="닉네임"
                />
            </InputContainer>
            <RowContainer>
                <Button onPress={createMember}>
                    <ButtonText>회원 가입</ButtonText>
                </Button>
                <Button>
                    <ButtonText>파일 업로드</ButtonText>
                </Button>
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
    background-color: #1B0C5D;
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
    background-color: #1B0C5D;
`;

const RowContainer = styled.View`
    flex-direction: row;
    justify-content: left;
    align-items: left;
    margin-top: 30px;
    margin-left: 20px;
`;
