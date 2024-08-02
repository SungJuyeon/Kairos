import React from "react";
import { SafeAreaView, ImageBackground, View, TouchableOpacity } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Home() {
    const backgroundImage = { uri: '../assets/Home.jpg' }; // 여기에 이미지 URL을 넣으세요.
    const { navigate } = useNavigation();

    return (
        <ImageBackground source={backgroundImage} style={{ flex: 1 }} resizeMode="cover">
            <Container>
                <Title>Hello</Title>
                <Title>Herobot!</Title>
                <CaptureButtonContainer>
                    <CaptureButtonStyle onPress={() => navigate('Control')}>
                        <CaptureButtonText>Herobot 제어하기</CaptureButtonText>
                    </CaptureButtonStyle>
                    <CaptureButtonStyle>
                        <CaptureButtonText>Smart Home 제어하기</CaptureButtonText>
                    </CaptureButtonStyle>
                </CaptureButtonContainer>
            </Container>
        </ImageBackground>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 50px;
    margin-bottom: 10px;
    font-weight: bold;
`;

const Container = styled.View`
    flex: 1;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0.3);
`;

const CaptureButtonContainer = styled.View`
    justify-content: center;
    align-items: center;
    margin-top: 20px;
`;

const CaptureButtonStyle = styled.TouchableOpacity`
    background-color: white;
    width: 300px;
    height: 60px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-top: 20px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 18px;
    font-weight: bold;
`;
