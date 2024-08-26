import React, { useState } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, Alert, PermissionsAndroid, Platform, Dimensions } from "react-native";
import CameraRoll from '@react-native-community/cameraroll';
import styled from 'styled-components/native';
import * as FileSystem from 'expo-file-system';


    // 스타일 컴포넌트를 위함
    const { width, height } = Dimensions.get('window');

    // 비율에 따른 스타일 조정
    const scale = width / 640; // 기준 너비에 대한 비율


export default function Control() {
    const [isUpPressed, setIsUpPressed] = useState(false);
    const [isLeftPressed, setIsLeftPressed] = useState(false);
    const [isRightPressed, setIsRightPressed] = useState(false);
    const [isDownPressed, setIsDownPressed] = useState(false);
    const [isCaptureVideoPressed, setIsCaptureVideoPressed] = useState(false);
    const [isOn, setIsOn] = useState(false); // on/off 상태 추가

    const [mostEmotion, setMostEmotion] = useState("Haapy");
    
    //const BASE_URL = 'http://172.30.1.36:8000'; // 라즈베리파이 서버 URL
    //const BASE_URL = 'http://172.20.10.4:8000'; // 라즈베리파이 서버 URL
    //const BASE_URL = 'http://223.194.136.129:8000'; // 라즈베리파이 서버 URL
    const BASE_URL = 'http://localhost:8000'; // 라즈베리파이 서버 URL

    const imageURL = '${BASE_URL}/video_feed';

    return (
        <Container>

            <Title>현재 나의 감정</Title>

                <ImageContainer>
                    <StyledImage
                        source={{ uri: `${BASE_URL}/video_feed` }}
                    />
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

const BorderContainer = styled.View`
    border: 1px solid #FFFFFF;
    width: ${width * 0.90}px;
    margin: 2%;
`;

const ImageContainer = styled.View`
    width: 90%;
    height: 35%;
    border-width: 2px; 
    border-color: #F8098B;
    background-color: #222222; 
    justify-content: center;
    align-items: center;
`;

const StyledImage = styled.Image`
    width: 100%;
    height: 100%;
`;

const Button = styled.TouchableOpacity`
    width: ${scale * 100}px; 
    height: ${scale * 50}px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isOn }) => (isOn ? '#AAAAAA' : '#F8098B')};
    border-radius: 10px;
    padding: 10px 10px;
    margin-left: 15px;
`;

const OnOffButtonText = styled.Text`
    color: white;
    font-size: ${scale * 18}px;
    font-weight: bold;
`;