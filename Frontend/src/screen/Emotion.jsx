import React, { useState, useEffect } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, Alert, Platform, Dimensions, ScrollView } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';

// 스타일 컴포넌트를 위함
const { width } = Dimensions.get('window');

const BASE_URL = 'http://10.0.2.2:8000';

export default function Control() {
    const { navigate } = useNavigation();

    const [mostEmotion, setMostEmotion] = useState("");
    const [emotionImage, setEmotionImage] = useState(null); // 감정 이미지를 저장할 상태 변수

    // 모스트 감정 가져오기
    const fetchMostEmotion = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');

            const response = await fetch(`${BASE_URL}/most_emotion`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'token': accessToken,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response Error:', errorText); // 오류 로그
                throw new Error('네트워크 응답이 좋지 않습니다.');
            }

            const data = await response.json(); // JSON으로 파싱

            // "most_frequent_emotion"의 값만 저장
            if (data.most_frequent_emotion) {
                setMostEmotion(data.most_frequent_emotion);
                // 감정 이미지를 가져오는 함수 호출
                fetchEmotionImage(data.most_frequent_emotion, accessToken);
            } else {
                console.warn('most_frequent_emotion이 없습니다.');
            }
        } catch (error) {
            console.error('Fetch Most Emotion Error:', error); // 전체 오류 로그
            Alert.alert('오류 발생', error.message);
        }
    };

    // 감정 이미지를 가져오는 함수
    const fetchEmotionImage = async (emotion, accessToken) => {
        try {
            const response = await fetch(`${BASE_URL}/most_emotion_pic`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'token': accessToken,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Image Response Error:', errorText); // 오류 로그
                throw new Error('이미지를 가져오는 데 실패했습니다.');
            }

            // 이미지 URL을 설정
            const imageUrl = URL.createObjectURL(await response.blob());
            setEmotionImage(imageUrl); // 감정 이미지를 상태에 저장
        } catch (error) {
            console.error('Fetch Emotion Image Error:', error); // 전체 오류 로그
            Alert.alert('오류 발생', error.message);
        }
    };

    useEffect(() => {
        fetchMostEmotion();
    }, []);

    return (
        <Container>
            <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', alignItems: 'center' }}>
                <RowContainer>
                    <Title>현재 나의 감정</Title>
                    <RepositoryButton onPress={() => navigate("Repository")}>
                        <RepositoryButtonText>
                            하이라이트 저장소
                        </RepositoryButtonText>
                    </RepositoryButton>
                </RowContainer>

                <ImageContainer>
                    {Platform.OS === 'web' ? (
                        <img src={emotionImage} width="100%" alt="Live Stream" />
                    ) : (
                        <StyledWebView
                            source={{ uri: `${BASE_URL}/video_feed/true` }}
                        />
                    )}
                </ImageContainer>
                <BorderContainer />

                <Title>오늘의 최다 감정 - {mostEmotion}</Title>
                <ImageContainer>
                    {emotionImage ? (
                        <StyledImage source={{ uri: emotionImage }} />
                    ) : (
                        <StyledImage source={{ uri: 'placeholder_image_url' }} /> // 기본 이미지 URL
                    )}
                </ImageContainer>
            </ScrollView>
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 20px;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
`;

const RowContainer = styled.View`
    background-color: #222222;
    flex-direction: row;
    justify-content: center;
    align-items: center;
`;

const BorderContainer = styled.View`
    border: 3px solid #ADCDFF;
    width: ${width * 0.90}px;
    margin-top: 20px;
    margin-bottom: 10px;
`;

const ImageContainer = styled.View`
    width: 90%;
    height: 34%;
    border-width: 2px; 
    border-color: #FFCEFF;
    background-color: #222222; 
`;

const StyledImage = styled.Image`
    width: 100%;
    height: 100%;
`;

const RepositoryButton = styled.TouchableOpacity`
    width: 150px; 
    height: 50px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isOn }) => (isOn ? '#AAAAAA' : '#FFCEFF')};
    border-radius: 10px;
    padding: 10px 10px;
    margin-left: 15px;
    margin-bottom: 15px;
`;

const RepositoryButtonText = styled.Text`
    color: black;
    font-size: 17px;
    font-weight: bold;
`;

const StyledWebView = styled(WebView)`
    flex: 1;
`;
