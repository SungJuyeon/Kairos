import React, { useContext } from "react";
import { View, Text, Image, SafeAreaView, TouchableOpacity, Alert, Platform } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';
import { WebView } from 'react-native-webview';

const BASE_URL = 'http://223.194.139.32:8000';

export default function Function4() {
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

            <ImageContainer>
                {Platform.OS === 'web' ? (
                    <img src={imageURL} width="100%" alt="Live Stream" />
                ) : (
                    <StyledWebView
                        source={{ uri: `${BASE_URL}/follow_video}` }}
                    />
                )}
            </ImageContainer>

            <CaptureButtonStyle onPress={() => handleMove("follow")}>
                <CaptureButtonText>음성 감지 시작</CaptureButtonText>
            </CaptureButtonStyle>
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 30px;
    margin-bottom: 10px;
    font-weight: bold;
    margin-bottom: 10px;
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

const ImageContainer = styled.View`
    width: 90%;
    height: 34%;
    border-width: 2px; 
    border-color: #FFCEFF;
    background-color: #222222; 
`;

const Margin2Container = styled.View`
    margin-top: 2%;
`;

const StyledWebView = styled(WebView)`
  flex: 1;
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
    margin: 20px;
    justify-content: center;
    align-items: center;
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