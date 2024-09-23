import React, { useState, useEffect } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, TextInput, FlatList, Text, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";


export default function VoiceChat() {
  const { navigate } = useNavigation();
  
  return (
    <Container>
        <ChatButton onPress={() => navigate("Chat")}>
          <ChatButtonText>가족 채팅방</ChatButtonText>
        </ChatButton>
    </Container>
  );
}

const Container = styled.SafeAreaView`
  background-color: #222222;
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
  background-color: #FFCEFF;
  padding: 12px 16px;
  border-radius: 16px;
`;

const ChatButtonText = styled.Text`
  color: #000;
  font-size: 26px;
  font-weight: bold;
`;
