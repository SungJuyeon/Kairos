import React, { useContext } from "react";
import { View, Text, Image, SafeAreaView, TouchableOpacity, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';

const BASE_URL = 'http://223.194.139.32:8000';

export default function Function3() {
    const { navigate } = useNavigation();

    const handleMove = async (start) => {
        try {
            const response = await fetch(`${BASE_URL}/${start}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            if (!response.ok) {
                throw new Error('네트워크 응답이 좋지 않습니다.');
            }
            const data = await response.json();
            Alert.alert("응답", JSON.stringify(data));
        } catch (error) {
            console.error(error);
            Alert.alert("오류", "요청 중 오류가 발생했습니다.");
        }
    };

    return (
        <Container>
            <Title>히어로봇 음성 감지 기능</Title>

            <Button onPress={() => handleMove("start_send_audio")}>
                <ButtonText>음성 감지 시작</ButtonText>
            </Button>

            <Button onPress={() => handleMove("sstop_send_audio")}>
                <ButtonText>음성 감지 정지</ButtonText>
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
