import React, { useContext } from "react";
import { View, Text, Image, SafeAreaView, TouchableOpacity, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';

const BASE_URL = 'http://172.30.1.55:8000';

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
                
            }
            const data = await response.json();
            
        } catch (error) {
            console.error(error);
            
        }
    };

    return (
        <Container>
            <Title>히어로봇 음성 감지 기능</Title>

            <CaptureButtonStyle2 onPress={() => handleMove("move/start_send_audio")}>
                <CaptureButtonText>음성 감지 시작</CaptureButtonText>
            </CaptureButtonStyle2>

            <CaptureButtonStyle3 onPress={() => handleMove("move/stop_send_audio")}>
                <CaptureButtonText>음성 감지 정지</CaptureButtonText>
            </CaptureButtonStyle3>

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

const RowButtonContainer = styled.View`
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
`;

const CaptureButtonStyle = styled.TouchableOpacity`
    background-color: #FFCEFF;
    width: 200px;
    height: 100px;
    border-radius: 10px;
    padding: 20px 20px;
    margin: 10px;
`;

const CaptureButtonStyle2 = styled.TouchableOpacity`
    background-color: white;
    width: 200px;
    height: 100px;
    border-radius: 10px;
    padding: 20px 20px;
    margin: 10px;
`;

const CaptureButtonStyle3 = styled.TouchableOpacity`
    background-color: #ADCDFF;
    width: 200px;
    height: 100px;
    border-radius: 10px;
    padding: 20px 20px;
    margin: 10px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 20px;
    font-weight: bold;
`;