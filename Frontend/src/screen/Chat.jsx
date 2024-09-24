import React, { useState, useEffect, useRef } from "react";
import { SafeAreaView, FlatList, Alert, KeyboardAvoidingView, Platform } from "react-native";
import styled from 'styled-components/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import jwt_decode from 'jwt-decode';

const BASE_URL = 'http://223.194.158.191:8080';
const WS_BASE_URL = 'ws://223.194.139.32:8000';

const WEBSOCKET_URL = `${WS_BASE_URL}/ws/chat`;
const MESSAGE_API_URL = `${BASE_URL}/messages`;

export default function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const websocketRef = useRef(null);
  const flatListRef = useRef(null);

  useEffect(() => {
    const fetchMessages = async () => {
      const accessToken = await AsyncStorage.getItem('token');
      const username = getUsernameFromToken(accessToken);

      try {
        const response = await fetch(`${MESSAGE_API_URL}/${username}`);
        const data = await response.json();
        if (data.messages) {
          const formattedMessages = data.messages.map(msg => ({
            text: msg.message,
            isUser: false
          }));
          setMessages(formattedMessages);

          setTimeout(() => {
            flatListRef.current.scrollToEnd({ animated: false });
          }, 100);
        }
      } catch (error) {
        console.error("메시지 로드 오류:", error);
      }
    };

    const connectWebSocket = async () => {
      const accessToken = await AsyncStorage.getItem('token');

      websocketRef.current = new WebSocket(WEBSOCKET_URL);

      websocketRef.current.onopen = () => {
        console.log("WebSocket 연결 성공");
        websocketRef.current.send(JSON.stringify({ token: accessToken }));
      };

      websocketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.sender_id) {
          const serverMessage = { text: data.message, isUser: false };
          setMessages((prevMessages) => [...prevMessages, serverMessage]);
          setTimeout(() => {
            flatListRef.current.scrollToEnd({ animated: true });
          }, 100);
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

    fetchMessages();
    connectWebSocket();

    // 5초마다 메시지를 새로 고침하는 타이머 설정
    const intervalId = setInterval(() => {
      fetchMessages();
    }, 5000);

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
      clearInterval(intervalId); // 컴포넌트 언마운트 시 타이머 정리
    };
  }, []);

  useEffect(() => {
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]);

  const getUsernameFromToken = (token) => {
    try {
      const payload = jwt_decode(token);
      return payload.username;
    } catch (error) {
      console.error("토큰에서 사용자 이름 추출 오류:", error);
      return null;
    }
  };

  const sendMessage = () => {
    if (message.trim() === '') return;

    const newMessage = { text: message, isUser: true };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setMessage('');

    const messageData = { message };
    if (websocketRef.current) {
      websocketRef.current.send(JSON.stringify(messageData));
    }

    setTimeout(() => {
      flatListRef.current.scrollToEnd({ animated: true });
    }, 100);
  };

  const handleSubmit = () => {
    sendMessage();
  };

  return (
    <KeyboardAvoidingView
      style={{ flex: 1 }}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
    >
      <Container>
        <ChatContainer>
          <FlatList
            ref={flatListRef}
            data={messages}
            keyExtractor={(item, index) => index.toString()}
            renderItem={({ item }) => (
              <MessageContainer isUser={item.isUser}>
                <MessageText isUser={item.isUser}>{item.text}</MessageText>
              </MessageContainer>
            )}
            inverted={false}
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
              <SendButtonText>전송</SendButtonText>
            </SendButton>
          </ButtonContainer>
        </InputContainer>
      </Container>
    </KeyboardAvoidingView>
  );
}

const Container = styled.SafeAreaView`
  background-color: #222222;
  flex: 1;
`;

const ChatContainer = styled.View`
  flex: 1;
  padding-top: 16px;
  padding-left: 16px;
  padding-right: 16px;
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
