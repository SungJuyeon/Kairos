import React, { useContext, useEffect, useState }from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Image, ScrollView, Alert } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function MyPage() {
    const { navigate } = useNavigation();
    const { logout } = useContext(AuthContext);
    const [username, setUsername] = useState('');
    const [photo, setPhoto] = useState('');


    const fetchUsername = async () => {
      try {
          const accessToken = await AsyncStorage.getItem('token');

          const response = await fetch('http://localhost:8080/user/username', {
              method: 'GET',
              headers: {
                  'Authorization': `Bearer ${accessToken}`,
                  'Content-Type': 'application/json',
              },
          });

          if (!response.ok) {
              throw new Error('네트워크 응답이 좋지 않습니다.');
          }

          const data = await response.text();
          setUsername(data);
      } catch (error) {
          Alert.alert('오류 발생', error.message);
      }
  };

  const fetchPhoto = async () => {
    try {
        const accessToken = await AsyncStorage.getItem('token');

        const response = await fetch('http://localhost:8080/user/photo', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('사진을 가져오는 데 실패했습니다. ');
        }

        const blob = await response.blob(); // Base64 문자열을 가져옵니다.
        const reader = new FileReader();

        reader.onloadend = () => {
          const base64data = reader.result; // Base64 문자열
          setPhoto(base64data); // 상태에 저장
      };

        reader.readAsDataURL(blob); // Blob을 Base64로 변환

    } catch (error) {
        Alert.alert('오류 발생', error.message);
    }
};

useEffect(() => {
  fetchUsername();
  fetchPhoto();
}, []);


    return (
        <Container>
          <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', alignItems: 'center' }}
          style={{ backgroundColor: '#222222' }}>

          <Title>{username || '로딩 중...'}님 반갑습니다!</Title>

          <Image
            source={{ uri: photo }}
            style={{ width: 300, height: 300, margin: 15 }}
          />
          <Button onPress={() => navigate('FamilyManage')}>
            <ButtonText>가족 관리</ButtonText>
          </Button>
          <Button onPress={() => navigate('ScheduleManage')}>
            <ButtonText>일정 관리</ButtonText>
          </Button>
          <LogoutButton onPress={() => logout()}>
            <LogoutButtonText>로그 아웃</LogoutButtonText>
          </LogoutButton>
          </ScrollView>
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 35px;
    margin-bottom: 40px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #1B0C5D;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const Button = styled.TouchableOpacity`
  background-color: #FFFFFF;
  padding: 10px 20px;
  border-radius: 5px;
  margin: 15px;
`;

const ButtonText = styled.Text`
  color: black;
  font-size: 24px;
  font-weight: bold;
`;

const LogoutButton = styled.TouchableOpacity`
  background-color: #FFCEFF;
  padding: 10px 20px;
  border-radius: 5px;
  margin: 15px;
`;

const LogoutButtonText = styled.Text`
  color: black;
  font-size: 16px;
  font-weight: bold;
`;