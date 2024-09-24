import React, { useContext }from "react";
import { View, Text, Image, SafeAreaView, TouchableOpacity } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';

const BASE_URL = 'http://223.194.139.32:8000';

export default function Function1() {
    const { navigate } = useNavigation();

    return (
        <Container>
            <Title>Herobot의 기능 1</Title>


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
  background-color: #FFFFFF;
  padding: 10px 20px;
  border-radius: 5px;
  margin: 5px;
`;

const ButtonText = styled.Text`
  color: black;
  font-size: 16px;
  font-weight: bold;
`;