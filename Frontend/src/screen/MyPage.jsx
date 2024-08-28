import React, { useContext }from "react";
import { View, Text, SafeAreaView, TouchableOpacity } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';

export default function MyPage() {
    const { navigate } = useNavigation();

    // 로그인 관련
    const { logout } = useContext(AuthContext);


    return (
        <Container>
          <Title>안녕하세요!</Title>
            <Button onPress={() => logout()}>
              <ButtonText>로그 아웃</ButtonText>
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
    background-color: #1B0C5D;
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