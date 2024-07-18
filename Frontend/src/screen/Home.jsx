import React from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Image } from "react-native";
import { useNavigation } from "@react-navigation/native";
import styled from 'styled-components/native'
import logo from "../../assets/ss.png"

export default function Home() {
    const { navigate } = useNavigation();

    return (
        <Container>
            <Title>안녕하세요!</Title>
            <Image source={logo} style={{ maxWidth:500, maxHeight: 700 }}/>
            <Button onPress={() => navigate("Search")}>
                <ButtonText>두번째 스크린으로 이동</ButtonText>
            </Button>
        </Container>
    );
}

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