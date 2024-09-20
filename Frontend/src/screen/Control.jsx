import React, { useState, useEffect } from "react";
import { View, Alert, Platform } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { WebView } from 'react-native-webview';
import axios from 'axios';

export default function Control() {
    const { navigate } = useNavigation();
    const [currentSpeed, setCurrentSpeed] = useState(50);

    const BASE_URL = 'http://localhost:8000'; // 라즈베리파이 서버 URL
    const imageURL = `${BASE_URL}/video`;

    const sendCommand = async (command) => {
        try {
            await axios.post(`${BASE_URL}/robot/command`, { command });
        } catch (error) {
            console.error('Error sending command:', error);
            Alert.alert('오류', '명령을 전송하는 데 실패했습니다.');
        }
    };

    const adjustSpeed = async (direction) => {
        const newSpeed = direction === 'up' ? Math.min(100, currentSpeed + 10) : Math.max(0, currentSpeed - 10);
        setCurrentSpeed(newSpeed);
        try {
            await axios.post(`${BASE_URL}/robot/speed`, { speed: newSpeed });
        } catch (error) {
            console.error('Error adjusting speed:', error);
            Alert.alert('오류', '속도를 조절하는 데 실패했습니다.');
        }
    };

    return (
        <Container>
            <Title>Herobot 제어</Title>
            <ImageContainer>
                {Platform.OS === 'web' ? (
                    <img src={imageURL} width="100%" alt="Live Stream" />
                ) : (
                    <StyledWebView source={{ uri: imageURL }} />
                )}
            </ImageContainer>
            <ControlContainer>
                <ControlButton onPress={() => sendCommand('forward')}>
                    <ButtonText>앞으로</ButtonText>
                </ControlButton>
                <ControlButton onPress={() => sendCommand('backward')}>
                    <ButtonText>뒤로</ButtonText>
                </ControlButton>
                <ControlButton onPress={() => sendCommand('left')}>
                    <ButtonText>왼쪽</ButtonText>
                </ControlButton>
                <ControlButton onPress={() => sendCommand('right')}>
                    <ButtonText>오른쪽</ButtonText>
                </ControlButton>
                <ControlButton onPress={() => sendCommand('stop')}>
                    <ButtonText>정지</ButtonText>
                </ControlButton>
            </ControlContainer>
            <SpeedContainer>
                <SpeedText>현재 속도: {currentSpeed}%</SpeedText>
                <SpeedButton onPress={() => adjustSpeed('up')}>
                    <ButtonText>속도 증가</ButtonText>
                </SpeedButton>
                <SpeedButton onPress={() => adjustSpeed('down')}>
                    <ButtonText>속도 감소</ButtonText>
                </SpeedButton>
            </SpeedContainer>
        </Container>
    );
}

const Container = styled.SafeAreaView`
    flex: 1;
    background-color: #222222;
    align-items: center;
    justify-content: center;
`;

const Title = styled.Text`
    color: white;
    font-size: 24px;
    margin-bottom: 20px;
`;

const ImageContainer = styled.View`
    width: 100%;
    height: 300px;
    margin-bottom: 20px;
`;

const StyledWebView = styled(WebView)`
    width: 100%;
    height: 100%;
`;

const ControlContainer = styled.View`
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    margin-bottom: 20px;
`;

const ControlButton = styled.TouchableOpacity`
    background-color: #4a4a4a;
    padding: 10px 20px;
    margin: 5px;
    border-radius: 5px;
`;

const SpeedContainer = styled.View`
    align-items: center;
`;

const SpeedText = styled.Text`
    color: white;
    font-size: 18px;
    margin-bottom: 10px;
`;

const SpeedButton = styled.TouchableOpacity`
    background-color: #4a4a4a;
    padding: 10px 20px;
    margin: 5px;
    border-radius: 5px;
`;

const ButtonText = styled.Text`
    color: white;
    font-size: 16px;
`;