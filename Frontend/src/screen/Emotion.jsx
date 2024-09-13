import React, { useState } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, Alert, PermissionsAndroid, Platform, Dimensions } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { WebView } from 'react-native-webview';


    // 스타일 컴포넌트를 위함
    const { width, height } = Dimensions.get('window');

    // 비율에 따른 스타일 조정
    const scale = width / 640; // 기준 너비에 대한 비율


export default function Control() {
    const { navigate } = useNavigation();

    const [mostEmotion, setMostEmotion] = useState("Haapy");
    

    const BASE_URL = 'http://localhost:8000'; // 라즈베리파이 서버 URL

    const imageURL = `${BASE_URL}/video`;

    return (
        <Container>
            
            <RowContainer>
            <Title>현재 나의 감정</Title>

            <RepositoryButton onPress={() => navigate("Repository")}>
                <RepositoryButtonText>
                    저장소
                </RepositoryButtonText>
            </RepositoryButton>

            </RowContainer>

                <ImageContainer>
                    {Platform.OS === 'web' ? (
                        <img src={imageURL} width="100%" alt="Live Stream" />
                    ) : (
                        <StyledWebView
                            source={{ uri: imageURL }}
                        />
                    )}
                </ImageContainer>
            <BorderContainer />



            <Title>오늘의 최다 감정: {mostEmotion}</Title>
                <ImageContainer>
                    <StyledImage
                        //source={{ uri: `` }} 최다 감정 사진 받아오기
                    />
                </ImageContainer>



        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 35px;
    font-weight: bold;
    margin-left: 20px;
`;

const Container = styled.SafeAreaView`
    background-color: #1B0C5D;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const RowContainer = styled.SafeAreaView`
    background-color: #1B0C5D;
    flex-direction: row;
    justify-content: center;
    align-items: center;
`;

const BorderContainer = styled.View`
    border: 1px solid #FFFFFF;
    width: ${width * 0.90}px;
    margin: 2%;
`;

const ImageContainer = styled.View`
    width: 90%;
    height: 34%;
    border-width: 2px; 
    border-color: #F8098B;
    background-color: #222222; 
`;

const StyledImage = styled.Image`
    width: 100%;
    height: 100%;
`;

const RepositoryButton = styled.TouchableOpacity`
    width: ${scale * 100}px; 
    height: ${scale * 50}px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isOn }) => (isOn ? '#AAAAAA' : '#F8098B')};
    border-radius: 10px;
    padding: 10px 10px;
    margin-left: 15px;
`;

const RepositoryButtonText = styled.Text`
    color: white;
    font-size: ${scale * 18}px;
    font-weight: bold;
`;


const StyledWebView = styled(WebView)`
  flex: 1;
`;
