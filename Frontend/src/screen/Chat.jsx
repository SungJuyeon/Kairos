import React, { useState, useRef } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, TextInput, FlatList, Text, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const { navigate } = useNavigation();
  const inputRef = useRef(null); // Input에 대한 ref 생성

  const BASE_URL = 'http://223.194.130.159:8000'; // 학교
  //const BASE_URL = 'http://localhost:8000'; // 라즈베리파이 서버 URL

  const imageURL = `${BASE_URL}/video_feed`;

  const sendMessage = async () => {
    if (message.trim() === '') return;

    const newMessage = { text: message, isUser: true };
    setMessages([newMessage, ...messages]);
    setMessage('');

    try {
      const response = await fetch('라즈베리파이 주소', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
        }),
      });

      const data = await response.text();

      if (response.ok) {
        handleSuccessMessage(data);
      } else {
        handleFailureMessage(data);
      }
    } catch (error) {
      console.error(error);
      Alert.alert('오류 발생', '다시 시도해 주세요.');
    } finally {
      // 메시지를 보낸 후에 포커스를 다시 설정합니다.
      inputRef.current.focus(); // 포커스 설정
    }
  };

  const handleSuccessMessage = (data) => {
    const serverMessage = { text: '메세지 수신 성공', isUser: false };
    setMessages((prevMessages) => [serverMessage, ...prevMessages]);
  };

  const handleFailureMessage = (data) => {
    const serverMessage = { text: '메세지 수신 실패', isUser: false };
    setMessages((prevMessages) => [serverMessage, ...prevMessages]);
  };

  const handleSubmit = () => {
    if (message.trim() !== '') {
      sendMessage();
      inputRef.current.focus(); // 메시지를 보낸 후 입력 필드에 포커스
    }
  };

  return (
    <Container>
      <Title>Herobot에게 물어보세요!</Title>
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
          ref={inputRef} // ref를 입력 필드에 연결
          value={message}
          onChangeText={setMessage}
          placeholder="메시지를 입력하세요"
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

const Title = styled.Text`
    color: white;
    font-size: 25px;
    font-weight: bold;
    margin-top: 5%;
    margin-left: 5%;
`;

const Container = styled.SafeAreaView`
  background-color: #1B0C5D;
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
  border-top-width: 1px;
  border-top-color: #FFFFFF;
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
