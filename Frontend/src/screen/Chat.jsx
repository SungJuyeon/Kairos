import React, { useState, useEffect, useRef } from "react";
import { SafeAreaView, View, TouchableOpacity, TextInput, FlatList, Text, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import AsyncStorage from '@react-native-async-storage/async-storage';

const WEBSOCKET_URL = "ws://localhost:8000/ws/chat"; // WebSocket 주소

export default function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const websocketRef = useRef(null);
  const { navigate } = useNavigation();

  useEffect(() => {
    const connectWebSocket = async () => {
      const accessToken = await AsyncStorage.getItem('token'); // AsyncStorage에서 JWT 토큰 가져오기
      console.log("토큰:", accessToken); // 토큰 확인 로그

      // WebSocket 연결 설정
      websocketRef.current = new WebSocket(WEBSOCKET_URL);
      console.log("웹소켓 연결 시도:", WEBSOCKET_URL); // 웹소켓 URL 로그

      websocketRef.current.onopen = () => {
        console.log("WebSocket 연결 성공");
        websocketRef.current.send(JSON.stringify({ token: accessToken }));
        console.log("토큰 전송:", accessToken); // 토큰 전송 로그
      };

      websocketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("서버로부터 메시지 수신:", data); // 수신한 메시지 로그
        if (data.message) {
          const serverMessage = { text: data.message, isUser: false };
          setMessages((prevMessages) => [serverMessage, ...prevMessages]);
        }
      };

      websocketRef.current.onerror = (error) => {
        console.error("WebSocket 오류:", error);
        Alert.alert('오류 발생', 'WebSocket 연결에 문제가 발생했습니다.');
      };

      websocketRef.current.onclose = () => {
        console.log("WebSocket 연결 종료");
      };
    };

    connectWebSocket();

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close(); // 컴포넌트 언마운트 시 WebSocket 연결 종료
      }
    };
  }, []);

  const sendMessage = () => {
    if (message.trim() === '') return;

    const newMessage = { text: message, isUser: true };
    setMessages((prevMessages) => [newMessage, ...prevMessages]);
    const messageData = { message };
    console.log("전송할 메시지 데이터:", messageData); // 전송할 메시지 로그
    if (websocketRef.current) {
      websocketRef.current.send(JSON.stringify(messageData));
    }
    setMessage('');
  };

  const handleSubmit = () => {
    sendMessage();
  };

  return (
    <Container>
      <ChatContainer>
        <FlatList
          data={messages}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <MessageContainer isUser={item.isUser}>
              <MessageText isUser={item.isUser}>{item.text}</MessageText>
            </MessageContainer>
          )}
          inverted
          contentContainerStyle={{ paddingVertical: 16 }}
          bounces={true}
          showsVerticalScrollIndicator={false}
        />
      </ChatContainer>
      <InputContainer>
        <StyledTextInput
          value={message}
          onChangeText={setMessage}
          placeholder="메시지를 입력하세요"
          placeholderTextColor={'#FFFFFF'}
          onSubmitEditing={handleSubmit}
          returnKeyType="send"
        />
        <ButtonContainer>
          <SendButton onPress={handleSubmit}>
            <SendButtonText>보내기</SendButtonText>
          </SendButton>
        </ButtonContainer>
      </InputContainer>
    </Container>
  );
}

const Container = styled.SafeAreaView`
  background-color: #222222;
  flex: 1;
`;

const ChatContainer = styled.View`
  flex: 1;
  padding: 16px;
`;

const MessageContainer = styled.View`
  align-self: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  background-color: ${props => props.isUser ? '#FFB0F9' : '#333'};
  padding: 12px;
  border-radius: 16px;
  max-width: 80%;
  margin-vertical: 4px;
`;

const MessageText = styled.Text`
  color: ${props => props.isUser ? '#000' : '#FFF'};
  font-size: 16px;
`;

const InputContainer = styled.View`
  flex-direction: row;
  align-items: center;
  padding: 16px;
  border-top-width: 3px;
  border-top-color: #ADCDFF;
`;

const ButtonContainer = styled.View`
  flex-direction: row;
  align-items: center;
  margin-left: 10px;
`;

const SendButton = styled.TouchableOpacity`
  background-color: #FFB0F9;
  padding: 12px 16px;
  border-radius: 16px;
  margin-right: 10px;
`;

const SendButtonText = styled.Text`
  color: #000;
  font-size: 16px;
`;

const StyledTextInput = styled.TextInput`
  flex: 1;
  padding-horizontal: 16px;
  height: 50px;
  color: #fff;
  font-size: 16px;
`;
