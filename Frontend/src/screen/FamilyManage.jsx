import React, { useEffect, useState } from "react";
import { Alert, FlatList, Image } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://172.30.1.55:8080';

export default function FamilyManage() {
    const { navigate } = useNavigation();
    const [data, setData] = useState([]);

    const fetchFamilyList = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');

            if (!accessToken) {
                throw new Error('토큰이 없습니다. 로그인 후 다시 시도해주세요.');
            }

            const response = await fetch(`${BASE_URL}/family/list`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`네트워크 응답이 좋지 않습니다: ${errorText}`);
            }

            const familyData = await response.json();
            setData(familyData);
        } catch (error) {
            Alert.alert('오류 발생', error.message);
        }
    };

    useEffect(() => {
        fetchFamilyList();
    }, []);

    const removeItem = async (nickname) => {
        try {
            const accessToken = await AsyncStorage.getItem('token');

            if (!accessToken) {
                throw new Error('토큰이 없습니다. 로그인 후 다시 시도해주세요.');
            }

            const response = await fetch(`${BASE_URL}/family/delete?memberUsername=${nickname}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`가족 구성원 삭제 실패: ${errorText}`);
            }

            const message = await response.text();
            Alert.alert('성공', message);

            // 가족 목록에서 해당 구성원 제거
            setData(prevData => prevData.filter(item => item.nickname !== nickname));
        } catch (error) {
            Alert.alert('오류 발생', error.message);
        }
    };

    const renderItem = ({ item }) => {
        const imageUri = item.photoname.startsWith('data:') ? item.photoname : `data:image/png;base64,${item.photoname}`;

        return (
            <Item>
                <ItemImage source={{ uri: imageUri }} />
                <ItemTextContainer>
                    <ItemText>{item.nickname}</ItemText>
                    <RemoveButton onPress={() => removeItem(item.nickname)}>
                        <RemoveButtonText>제거</RemoveButtonText>
                    </RemoveButton>
                </ItemTextContainer>
            </Item>
        );
    };

    return (
        <Container>
            <Title>가족 관리</Title>
            <FlatList
                data={data}
                renderItem={renderItem}
                keyExtractor={(item, index) => item.nickname}
                contentContainerStyle={{ paddingBottom: 20 }}
            />
            <RowContainer>
                <Button onPress={() => navigate('FamilyAdd')}>
                    <ButtonText>초대하기</ButtonText>
                </Button>
                <Button3 onPress={() => navigate('FamilyReceive')}>
                    <ButtonText>수락하기</ButtonText>
                </Button3>
            </RowContainer>
        </Container>
    );
}

// Styled components remain the same
const Title = styled.Text`
    color: white;
    font-size: 30px;
    margin-bottom: 10px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: center;
    align-items: center;
    padding: 10px;
`;

const Item = styled.View`
    background-color: #FFFFFF;
    padding: 15px;
    border-radius: 5px;
    margin: 5px;
    width: 300px;
    flex-direction: row; /* 수평 방향으로 배치 */
    align-items: center; /* 세로 중앙 정렬 */
`;

const ItemImage = styled.Image`
    width: 80px;
    height: 80px;
    border-radius: 40px;
    margin-right: 10px; /* 이미지와 텍스트 사이의 여백 추가 */
`;

const ItemTextContainer = styled.View`
    flex: 1; /* 남는 공간을 모두 사용 */
    flex-direction: row; /* 텍스트와 버튼을 수평으로 배치 */
    justify-content: space-between; /* 텍스트와 버튼 간의 공간을 최대로 */
    align-items: center; /* 세로 중앙 정렬 */
`;

const ItemText = styled.Text`
    color: black;
    font-size: 16px;
    font-weight: bold;
`;

const RemoveButton = styled.TouchableOpacity`
    background-color: #FF4D4D;
    padding: 5px 10px;
    border-radius: 5px;
`;

const RemoveButtonText = styled.Text`
    color: white;
    font-weight: bold;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFCEFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 10px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 18px;
    font-weight: bold;
`;

const RowContainer = styled.View`
    flex-direction: row;
    justify-content: left;
    align-items: left;
    margin-top: 30px;
    margin-left: 20px;
    margin-bottom: 30px;
`;

const Button3 = styled.TouchableOpacity`
    background-color: #ADCDFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 10px;
`;
