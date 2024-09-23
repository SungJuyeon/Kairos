import React, { useState, useEffect, useRef } from "react";
import { SafeAreaView, FlatList, Alert } from "react-native";
import styled from 'styled-components/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import jwt_decode from 'jwt-decode'; // jwt-decode 라이브러리 추가

const WEBSOCKET_URL = "ws://localhost:8000/ws/chat"; // WebSocket 주소
const MESSAGE_API_URL = "http://localhost:8000/messages"; // 메시지를 가져오는 API URL

export default function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const websocketRef = useRef(null);
  const flatListRef = useRef(null); // FlatList reference 추가

  useEffect(() => {
    const fetchMessages = async () => {
      const accessToken = await AsyncStorage.getItem('token');
      const username = getUsernameFromToken(accessToken); // JWT에서 username 가져오기

      try {
        const response = await fetch(`${MESSAGE_API_URL}/${username}`);
        const data = await response.json();
        if (data.messages) {
          const formattedMessages = data.messages.map(msg => ({
            text: msg.message,
            isUser: false // 서버에서 온 메시지로 표시
          }));
          setMessages(formattedMessages); // 초기 메시지를 설정

          // 메시지를 불러온 후 스크롤을 가장 아래로 내리기
          setTimeout(() => {
            flatListRef.current.scrollToEnd({ animated: false });
          }, 100); // 약간의 지연을 두고 스크롤
        }
      } catch (error) {
        console.error("메시지 로드 오류:", error);
      }
    };

    const connectWebSocket = async () => {
      const accessToken = await AsyncStorage.getItem('token');

      // WebSocket 연결 설정
      websocketRef.current = new WebSocket(WEBSOCKET_URL);

      websocketRef.current.onopen = () => {
        console.log("WebSocket 연결 성공");
        websocketRef.current.send(JSON.stringify({ token: accessToken }));
      };

      websocketRef.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.sender_id) {
          const serverMessage = { text: data.message, isUser: false };
          // 메시지를 즉시 화면에 추가
          setMessages((prevMessages) => [...prevMessages, serverMessage]); // 아래로 추가
          // 새로운 메시지가 추가되면 스크롤을 가장 아래로 내리기
          setTimeout(() => {
            flatListRef.current.scrollToEnd({ animated: true });
          }, 100); // 약간의 지연을 두고 스크롤
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

    fetchMessages(); // 기존 메시지 로드
    connectWebSocket();

    return () => {
      if (websocketRef.current) {
        websocketRef.current.close(); // 컴포넌트 언마운트 시 WebSocket 연결 종료
      }
    };
  }, []);

  useEffect(() => {
    // messages가 변경될 때마다 스크롤을 가장 아래로 내리기
    if (flatListRef.current) {
      flatListRef.current.scrollToEnd({ animated: true });
    }
  }, [messages]); // messages가 변경될 때마다 실행

  const getUsernameFromToken = (token) => {
    try {
      console.log("Received token:", token); // 토큰 로그
      const payload = jwt_decode(token); // jwt-decode 라이브러리 사용
      console.log("Decoded payload:", payload); // 디코딩된 페이로드 로그
      return payload.username; // username 반환
    } catch (error) {
      console.error("토큰에서 사용자 이름 추출 오류:", error);
      return null;
    }
  };

  const sendMessage = () => {
    if (message.trim() === '') return;

    const newMessage = { text: message, isUser: true };
    setMessages((prevMessages) => [...prevMessages, newMessage]); // 아래로 추가
    setMessage('');

    const messageData = { message };
    if (websocketRef.current) {
      websocketRef.current.send(JSON.stringify(messageData));
    }

    // 메시지를 보낸 후 스크롤을 가장 아래로 내리기
    setTimeout(() => {
      flatListRef.current.scrollToEnd({ animated: true });
    }, 100); // 약간의 지연을 두고 스크롤
  };

  const handleSubmit = () => {
    sendMessage();
  };

  return (
    <Container>
      <ChatContainer>
        <FlatList
          ref={flatListRef} // FlatList에 ref 추가
          data={messages}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <MessageContainer isUser={item.isUser}>
              <MessageText isUser={item.isUser}>{item.text}</MessageText>
            </MessageContainer>
          )}
          inverted={false} // inverted를 false로 설정
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
