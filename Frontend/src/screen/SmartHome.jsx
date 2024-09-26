import React, { useContext } from "react";
import { View, Text, Image, SafeAreaView, TouchableOpacity, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';

const BASE_URL = 'http://172.30.1.68:8000';
export default function SmartHome() {
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
        
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <Container>
            <Title>원격 스마트홈 시스템</Title>

            <RowButtonContainer>
                <CaptureButtonStyle2 onPress={() => handleMove("home_control/led/true")}>
                    <CaptureButtonText>조명 켜기</CaptureButtonText>
                </CaptureButtonStyle2>
                <CaptureButtonStyle3 onPress={() => handleMove("home_control/led/false")}>
                    <CaptureButtonText>조명 끄기</CaptureButtonText>
                </CaptureButtonStyle3>
            </RowButtonContainer>


            <RowButtonContainer>
                <CaptureButtonStyle onPress={() => handleMove("home_control/induction/true")}>
                    <CaptureButtonText>인뎍션 켜기</CaptureButtonText>
                </CaptureButtonStyle>
                <CaptureButtonStyle2 onPress={() => handleMove("home_control/induction/false")}>
                    <CaptureButtonText>인덕션 끄기</CaptureButtonText>
                </CaptureButtonStyle2>
            </RowButtonContainer>

            <RowButtonContainer>
                <CaptureButtonStyle2 onPress={() => handleMove("home_control/relay/true")}>
                    <CaptureButtonText>선풍기 켜기</CaptureButtonText>
                </CaptureButtonStyle2>
                <CaptureButtonStyle3 onPress={() => handleMove("home_control/relay/false")}>
                    <CaptureButtonText>선풍기 끄기</CaptureButtonText>
                </CaptureButtonStyle3>
            </RowButtonContainer>


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
    width: 140px;
    height: 100px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-left: 10px;
    margin-right: 10px;
`;

const CaptureButtonStyle2 = styled.TouchableOpacity`
    background-color: white;
    width: 140px;
    height: 100px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-left: 10px;
    margin-right: 10px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 20px;
    font-weight: bold;
`;

const CaptureButtonStyle3 = styled.TouchableOpacity`
    background-color: #ADCDFF;
    width: 140px;
    height: 100px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-left: 10px;
    margin-right: 10px;
`;