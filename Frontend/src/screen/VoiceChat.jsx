import React, { useState, useEffect } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, TextInput, FlatList, Text, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import * as Speech from 'expo-speech'; // Import the Expo Speech API

export default function VoiceChat() {
  const { navigate } = useNavigation();
  
  // 음성 인식 상태를 관리하는 state 변수
  const [isListening, setIsListening] = useState(false);
  // 인식된 텍스트를 저장하는 state 변수
  const [recognizedText, setRecognizedText] = useState('');

  // 음성 인식이 시작될 때 호출되는 함수
  const onSpeechStartHandler = () => {
    setIsListening(true);
  }

  // 음성 인식이 끝날 때 호출되는 함수
  const onSpeechEndHandler = () => {
    setIsListening(false);
    sendTextToServer(recognizedText);
  }

  // 음성 인식을 시작하는 함수
  const startVoiceRecognition = async () => {
    try {
      // Expo Speech API를 사용하여 음성 인식 권한 요청
      const { granted } = await Speech.requestSpeechPermissionsAsync();
      if (granted) {
        // 음성 인식 시작
        const result = await Speech.startSpeechRecognitionAsync();
        setRecognizedText(result.transcription);
        onSpeechEndHandler();
      } else {
        // 권한이 거부된 경우 경고 메시지 표시
        Alert.alert('Permission denied', 'Please grant speech recognition permission to use this feature.');
      }
    } catch (error) {
      console.error('Error with speech recognition:', error);
    }
  }

  // 인식된 텍스트를 서버로 전송하는 함수
  const sendTextToServer = (text) => {
    console.log('Sending text to server:', text);
  }

  return (
    <Container>
      {/* 음성 인식 버튼 */}
      <CenterButton onPress={startVoiceRecognition}>
        <CenterButtonText>{isListening ? '음성인식 중입니다...' : 'Voice Chat'}</CenterButtonText>
      </CenterButton>
      {/* 채팅 모드 버튼 */}
      <ChatButtonContainer>
        <ChatButton onPress={() => navigate("Chat")}>
          <ChatButtonText>가족과 채팅 하러 가기</ChatButtonText>
        </ChatButton>
      </ChatButtonContainer>
    </Container>
  );
}

const Container = styled.SafeAreaView`
  background-color: #1B0C5D;
  flex: 1;
  justify-content: center;
  align-items: center;
`;

const CenterButton = styled.TouchableOpacity`
  width: 250px;
  height: 250px;
  border-radius: 150px;
  background-color: #FFB0F9;
  justify-content: center;
  align-items: center;
`;

const CenterButtonText = styled.Text`
  color: #000;
  font-size: 24px;
  font-weight: bold;
`;

const ChatButtonContainer = styled.View`
  position: absolute;
  bottom: 20px;
  right: 20px;
`;

const ChatButton = styled.TouchableOpacity`
  background-color: #999;
  padding: 12px 16px;
  border-radius: 16px;
`;

const ChatButtonText = styled.Text`
  color: #fff;
  font-size: 16px;
`;
