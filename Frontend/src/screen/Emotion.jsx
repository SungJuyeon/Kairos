import React, { useState, useEffect } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, Alert, Platform, Dimensions } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { WebView } from 'react-native-webview';
import axios from 'axios';

const { width, height } = Dimensions.get('window');
const scale = width / 640;

export default function Emotion() {
    const { navigate } = useNavigation();
    const [currentEmotion, setCurrentEmotion] = useState("Unknown");
    const [mostEmotion, setMostEmotion] = useState("Happy");
    const [mostEmotionImage, setMostEmotionImage] = useState(null);

    const BASE_URL = 'http://223.194.136.129:8000';
    const imageURL = `${BASE_URL}/video`;

    useEffect(() => {
        const fetchEmotionData = async () => {
            try {
                const response = await axios.get(`${BASE_URL}/emotion`);
                setCurrentEmotion(response.data.current_emotion);
                setMostEmotion(response.data.most_frequent_emotion);
                setMostEmotionImage(response.data.most_frequent_emotion_image);
            } catch (error) {
                console.error('Error fetching emotion data:', error);
                Alert.alert('오류', '감정 데이터를 가져오는데 실패했습니다.');
            }
        };

        fetchEmotionData();
        const interval = setInterval(fetchEmotionData, 5000); // 5초마다 업데이트

        return () => clearInterval(interval);
    }, []);

    return (
        <Container>
            <RowContainer>
                <Title>현재 나의 감정</Title>
                <RepositoryButton onPress={() => navigate("Highlight")}>
                    <RepositoryButtonText>하이라이트</RepositoryButtonText>
                </RepositoryButton>
            </RowContainer>

            <ImageContainer>
                {Platform.OS === 'web' ? (
                    <img src={imageURL} width="100%" alt="Live Stream" />
                ) : (
                    <StyledWebView source={{ uri: imageURL }} />
                )}
            </ImageContainer>
            <EmotionText>현재 감정: {currentEmotion}</EmotionText>
            <BorderContainer />

            <Title>오늘의 최다 감정: {mostEmotion}</Title>
            <ImageContainer>
                {mostEmotionImage && (
                    <StyledImage source={{ uri: mostEmotionImage }} />
                )}
            </ImageContainer>
        </Container>
    );
}

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: flex-start;
    align-items: center;
    padding-top: 50px;
`;

const RowContainer = styled.View`
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding: 0 20px;
`;

const Title = styled.Text`
    color: white;
    font-size: 24px;
    font-weight: bold;
`;

const RepositoryButton = styled.TouchableOpacity`
    background-color: #FFB0F9;
    padding: 10px 20px;
    border-radius: 5px;
`;

const RepositoryButtonText = styled.Text`
    color: black;
    font-size: 16px;
    font-weight: bold;
`;

const ImageContainer = styled.View`
    width: 90%;
    height: ${height * 0.3}px;
    margin: 20px 0;
`;

const StyledWebView = styled(WebView)`
    width: 100%;
    height: 100%;
`;

const StyledImage = styled.Image`
    width: 100%;
    height: 100%;
    resize-mode: contain;
`;

const EmotionText = styled.Text`
    color: white;
    font-size: 18px;
    margin-top: 10px;
`;

const BorderContainer = styled.View`
    width: 90%;
    height: 1px;
    background-color: white;
    margin: 20px 0;
`;
