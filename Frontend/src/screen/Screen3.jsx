import React from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Image } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import logo from "../../assets/ss5.png"

export default function Store() {
    const { navigate } = useNavigation();

    return (
        <Container>
            <Image source={logo} style={{ maxWidth:500, maxHeight: 700 }}/>
            <Button onPress={() => navigate("Search")}>
                <ButtonText>뒤로 가기</ButtonText>
            </Button>
        </Container>
    );
}

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