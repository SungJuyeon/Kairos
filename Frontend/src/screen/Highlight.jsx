import React, { useContext }from "react";
import { View, Text, Image, SafeAreaView, TouchableOpacity } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';


export default function Highlight() {
    const { navigate } = useNavigation();

    //const BASE_URL = 'http://172.30.1.36:8000'; // 라즈베리파이 서버 URL
    //const BASE_URL = 'http://172.20.10.4:8000'; // 라즈베리파이 서버 URL
    const BASE_URL = 'http://223.194.158.191:8000';

    return (
        <Container>
            <Title>Herobot이 만든</Title>
            <Title>하이라이트 영상</Title>


            <Button onPress={() => navigate("Emotion")}>
              <ButtonText>감정 보러가기</ButtonText>
            </Button>
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 30px;
    margin-bottom: 10px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const Button = styled.TouchableOpacity`
  background-color: #FFB0F9;
  padding: 10px 20px;
  border-radius: 5px;
  margin: 5px;
`;

const ButtonText = styled.Text`
  color: black;
  font-size: 16px;
  font-weight: bold;
`;