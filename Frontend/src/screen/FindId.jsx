import React, { useState }  from "react";
import { View, Text, SafeAreaView, TouchableOpacity, TextInput } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";

export default function FindId() {
    const { navigate } = useNavigation();

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');

    // TextInput이 포커싱 되었을 때 색상 변경
    const [nameFocused, setNameFocused] = useState(false);
    const [emailFocused, setEmailFocused] = useState(false);

    // 아이디 찾기 버튼 클릭 시
    const findId = async () => {
        try {
            const userData = { name: name, email: email }
            const response = await axios.post('http://localhost:8080/find/id', userData, {
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                // 아이디 찾기 성공 처리
                console.log(response.data);
            });
        // 아이디 찾기 실패
        } catch (error) {   
            console.error('아이디를 찾을 수 없습니다.', error);
        }
        };

    return (
        <Container>
            <Title>아이디 찾기</Title>
            <InputContainer>
            <Text style={{ color: 'white', fontWeight: 'bold' }}>이름</Text>
            <StyledTextInput
                onChangeText={text => setName(text)}
                value={name}
                onFocus={() => setNameFocused(true)}
                onBlur={() => setNameFocused(false)}
                focused={nameFocused}
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
                />
                </InputContainer>
            <RowContainer>
                <Button onPress={findId}>
                    <ButtonText>아이디 찾기</ButtonText>
                </Button>
                <BackButton onPress={() => navigate("FindUserData")}>
                    <ButtonText>뒤로 가기</ButtonText>
                </BackButton>
            </RowContainer>
        </Container>
    )
}

const Container = styled.SafeAreaView`
    background-color: #000000;
    flex: 1;
    padding: 5%;
    justify-content: center;
    align-items: center;
`;

const Title = styled.Text`
    color: white;
    font-size: 30px;
    margin-bottom: 40px;
    font-weight: bold;
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
    margin-top: 20px;
`;

const InputContainer = styled.View`
    width: 100%;
    padding: 0 20px;
    margin-left: 25%;
`;