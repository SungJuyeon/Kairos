import React, { useState, useEffect } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, Alert, PermissionsAndroid, Platform, Dimensions } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { WebView } from 'react-native-webview';
import AsyncStorage from '@react-native-async-storage/async-storage';


    // 스타일 컴포넌트를 위함
    const { width, height } = Dimensions.get('window');

    // 비율에 따른 스타일 조정
    const scale = width / 640; // 기준 너비에 대한 비율


export default function Control() {
    const { navigate } = useNavigation();

    const [mostEmotion, setMostEmotion] = useState("Happy");
    

    // const BASE_URL = 'http://localhost:8000'; // 라즈베리파이 서버 URL
    // const imageURL = `${BASE_URL}/video`;

    // 모스트 감정 가져오기
    const fetchMostEmotion = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');
            console.log('Access Token:', accessToken); // Access Token 로그
    
            const response = await fetch('http://localhost:8000/most_emotion', {
                method: 'GET',
                headers: {
                    'token': accessToken, // 'Authorization' 대신 'token' 헤더 사용
                    'Content-Type': 'application/json',
                },
            });
    
            console.log('Response Status:', response.status); // 응답 상태 로그
    
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response Error:', errorText); // 오류 로그
                throw new Error('네트워크 응답이 좋지 않습니다.');
            }
    
            const data = await response.text();
            console.log('Most Emotion Data:', data); // 받아온 데이터 로그
            setMostEmotion(data);
        } catch (error) {
            console.error('Fetch Most Emotion Error:', error); // 전체 오류 로그
            Alert.alert('오류 발생', error.message);
        }
    };

    useEffect(() => {
        fetchMostEmotion();
      }, []);
      

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
                    ) : Platform.OS === 'android' ? (
                        <StyledWebView
                            source={{ uri: 'http://localhost:8000/video_feed/true' }}
                        />
                    ) : (
                        <StyledWebView
                            source={{ uri: 'http://localhost:8000/video_feed/true' }}
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
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 20px;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const RowContainer = styled.SafeAreaView`
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
    width: ${scale * 100}px; 
    height: ${scale * 50}px;
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
    font-size: ${scale * 18}px;
    font-weight: bold;
`;


const StyledWebView = styled(WebView)`
  flex: 1;
`;
