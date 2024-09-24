import React, { useContext, useEffect, useState } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Image, ScrollView, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { AuthContext } from './AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://223.194.139.32:8080';

export default function MyPage() {
    const { navigate } = useNavigation();
    const { logout } = useContext(AuthContext);
    const [username, setUsername] = useState('');
    const [photo, setPhoto] = useState('');

    const fetchUsername = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');

            const response = await fetch(`${BASE_URL}/user/username`, {
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

            const response = await fetch(`${BASE_URL}/user/photo`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('사진을 가져오는 데 실패했습니다.');
            }

            const blob = await response.blob();
            const reader = new FileReader();

            reader.onloadend = () => {
                const base64data = reader.result;
                setPhoto(base64data);
            };

            reader.readAsDataURL(blob);

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
            <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', alignItems: 'center' }} style={{ backgroundColor: '#222222' }}>
                <Title>{username || '로딩 중...'}님 반갑습니다!</Title>

                <ProfileImage
                    source={{ uri: photo }}
                />
                <RowButtonContainer>
                    <CaptureButtonStyle2 onPress={() => navigate('FamilyManage')}>
                        <ButtonText>가족 관리</ButtonText>
                    </CaptureButtonStyle2>
                    <CaptureButtonStyle2 onPress={() => navigate('ScheduleManage')}>
                        <ButtonText>일정 관리</ButtonText>
                    </CaptureButtonStyle2>
                </RowButtonContainer>
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

const ProfileImage = styled.Image`
    width: 300px;
    height: 300px;
    margin: 15px;
    border-radius: 150px;
`;

const LogoutButton = styled.TouchableOpacity`
    width: 130px;
    height: 60px;
    background-color: #FFCEFF;
    border-radius: 10px;
    margin: 15px;
    padding: 0; /* 내부 패딩을 제거하여 중앙 정렬 */
    justify-content: center; /* 텍스트 중앙 정렬 */
    align-items: center; /* 텍스트 중앙 정렬 */
`;

const LogoutButtonText = styled.Text`
    color: black;
    font-size: 20px;
    font-weight: bold;
`;

const RowButtonContainer = styled.View`
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
`;

const CaptureButtonStyle2 = styled.TouchableOpacity`
    background-color: white;
    width: 140px;
    height: 70px;
    border-radius: 10px;
    padding: 0; /* 내부 패딩을 제거하여 중앙 정렬 */
    margin-left: 10px;
    margin-right: 10px;
    justify-content: center; /* 텍스트 중앙 정렬 */
    align-items: center; /* 텍스트 중앙 정렬 */
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 24px;
    font-weight: bold;
`;
