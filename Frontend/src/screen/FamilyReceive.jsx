import React, { useEffect, useState } from "react";
import { Alert, FlatList } from "react-native";
import styled from 'styled-components/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL = 'http://10.0.2.2:8080';

export default function FamilyReceive() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchReceivedRequests = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');

            if (!accessToken) {
                throw new Error('토큰이 없습니다. 로그인 후 다시 시도해주세요.');
            }

            const response = await fetch(`${BASE_URL}/family/requests/received`, {
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

            const data = await response.json();
            setRequests(data);
        } catch (error) {
            Alert.alert('오류 발생', error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleAccept = async (requestId) => {
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch(`${BASE_URL}/family/request/accept?requestId=${requestId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`수락 요청 실패: ${errorText}`);
            }

            Alert.alert('요청 수락', '가족 요청이 수락되었습니다.');
            fetchReceivedRequests(); // 요청 목록 새로 고침
        } catch (error) {
            Alert.alert('오류 발생', error.message);
        }
    };

    const handleReject = async (requestId) => {
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch(`${BASE_URL}/family/request/reject?requestId=${requestId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`거절 요청 실패: ${errorText}`);
            }

            Alert.alert('요청 거절', '가족 요청이 거절되었습니다.');
            fetchReceivedRequests(); // 요청 목록 새로 고침
        } catch (error) {
            Alert.alert('오류 발생', error.message);
        }
    };

    useEffect(() => {
        fetchReceivedRequests();
    }, []);

    const renderItem = ({ item }) => (
        <RequestItem>
            <RequestText>보낸 사람: {item.senderUsername}</RequestText>
            <RequestText>상태: {item.status === 'PENDING' ? '수락 대기중' : item.status}</RequestText>
            <ButtonContainer>
                <AcceptButton onPress={() => handleAccept(item.requestId)}>
                    <ButtonText>수락</ButtonText>
                </AcceptButton>
                <RejectButton onPress={() => handleReject(item.requestId)}>
                    <ButtonText>거절</ButtonText>
                </RejectButton>
            </ButtonContainer>
        </RequestItem>
    );

    if (loading) {
        return <Container><RequestText>로딩 중...</RequestText></Container>;
    }

    return (
        <Container>
            <Title>가족 요청</Title>
            <FlatList
                data={requests}
                renderItem={renderItem}
                keyExtractor={(item) => item.requestId ? item.requestId.toString() : Math.random().toString()} // requestId 사용
            />
            <RefreshButton onPress={fetchReceivedRequests}>
                <RefreshButtonText>새로 고침</RefreshButtonText>
            </RefreshButton>
        </Container>
    );
};

const Container = styled.SafeAreaView`
    flex: 1;
    padding: 10px;
    background-color: #222222;
`;

const Title = styled.Text`
    color: white;
    font-size: 36px;
    font-weight: bold;
    margin-bottom: 10px;
    text-align: center; /* 중앙 정렬 */
`;

const RequestItem = styled.View`
    padding: 10px;
    border-bottom-width: 1px;
    border-bottom-color: #ccc;
    background-color: white;
    margin-bottom: 5px;
    border-radius: 10px; /* 모서리 둥글게 만들기 */
`;

const RequestText = styled.Text`
    font-size: 18px; /* 폰트 사이즈를 크게 설정 */
    font-weight: bold; /* 폰트 웨이트를 bold로 설정 */
`;

const ButtonContainer = styled.View`
    flex-direction: row;
    justify-content: space-between;
    margin-top: 10px;
`;

const AcceptButton = styled.TouchableOpacity`
    background-color: #4CAF50; /* 수락 버튼 색상 */
    padding: 10px;
    border-radius: 5px;
    flex: 1;
    margin-right: 5px;
`;

const RejectButton = styled.TouchableOpacity`
    background-color: #FF4D4D; /* 거절 버튼 색상 */
    padding: 10px;
    border-radius: 5px;
    flex: 1;
`;

const ButtonText = styled.Text`
    color: white;
    text-align: center;
`;

const RefreshButton = styled.TouchableOpacity`
    background-color: #FFCEFF; /* 새로 고침 버튼 색상 */
    padding: 12px 24px;
    border-radius: 10px;
    margin-top: 20px;
    margin-bottom: 10px;
    align-items: center; /* 텍스트 중앙 정렬 */
`;

const RefreshButtonText = styled.Text`
    color: black;
    font-size: 20px;
    font-weight: bold;
`;
