import React, { useState } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, TextInput, FlatList, Text, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const { navigate } = useNavigation();

  // 다시 inputText를 포커싱하기 위해
  //const inputText = document.getElementById('inputText');

  // 서버에 메세지를 보내는 함수
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

      // 답장이 왔을 때
      if (response.ok) {
        handleSuccessMessage(data);
      } else {
        handleFailureMessage(data);
      }
    } catch (error) {
      console.error(error);
      Alert.alert('오류 발생', '다시 시도해 주세요.');
    }
  };

  // 메세지가 수신 되었을 때
  const handleSuccessMessage = (data) => {
    const serverMessage = { text: '메세지 수신 성공', isUser: false };
    setMessages((prevMessages) => [serverMessage, ...prevMessages]);
  };

  // 메세지 수신이 실패했을 때
  const handleFailureMessage = (data) => {
    const serverMessage = { text: '메세지 수신 실패', isUser: false };
    setMessages((prevMessages) => [serverMessage, ...prevMessages]);
  };

  // 보내기 버튼 혹은 엔터키를 눌렀을 때
  const handleSubmit = () => {
    if (message.trim() !== '') {
      sendMessage();
      //inputText.focus();
    }
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
          onSubmitEditing={handleSubmit} // 엔터키를 누르면 보내기 버튼 클릭 처리
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

const VoiceButton = styled.TouchableOpacity`
  background-color: #999;
  padding: 12px 16px;
  border-radius: 16px;
`;

const VoiceButtonText = styled.Text`
  color: #fff;
  font-size: 16px;
`;

const StyledTextInput = styled.TextInput`
  flex: 1;
  padding-horizontal: 16px;
  height: 50px;
  color: #fff;
  font-size: 16px;
`;
