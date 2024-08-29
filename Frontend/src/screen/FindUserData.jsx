import React, { useState }  from "react";
import { View, Text, SafeAreaView, TouchableOpacity, TextInput } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";

export default function FindUserData() {
    const { navigate } = useNavigation();

    return (
        <Container>
            <Title>아이디 혹은 비밀번호 찾기</Title>
                <Button onPress={() => navigate("FindId")}>
                    <ButtonText>아이디 찾기</ButtonText>
                </Button>
                <Button onPress={() => navigate("FindPassword")}>
                    <ButtonText>비밀번호 찾기</ButtonText>
                </Button>
        </Container>
    )
}

const Container = styled.SafeAreaView`
    background-color: #1B0C5D;
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
    margin: 20px;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 20px;
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