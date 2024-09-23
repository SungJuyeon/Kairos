import React, { useEffect, useState } from "react";
import { Alert, FlatList } from "react-native";
import styled from 'styled-components/native';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function FamilyReceive() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchReceivedRequests = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');

            if (!accessToken) {
                throw new Error('토큰이 없습니다. 로그인 후 다시 시도해주세요.');
            }

            const response = await fetch('http://localhost:8080/family/requests/received', {
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
        // 수락 요청 처리
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch(`http://localhost:8080/family/request/accept?requestId=${requestId}`, {
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
        // 거절 요청 처리
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch(`http://localhost:8080/family/request/reject?requestId=${requestId}`, {
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
            <RequestText>상태: {item.status}</RequestText>
            <RequestText>RequestId: {item.requestId}</RequestText>
            <ButtonContainer>
                <ActionButton onPress={() => handleAccept(item.requestId)}>
                    <ButtonText>수락</ButtonText>
                </ActionButton>
                <ActionButton onPress={() => handleReject(item.requestId)}>
                    <ButtonText>거절</ButtonText>
                </ActionButton>
            </ButtonContainer>
        </RequestItem>
    );

    if (loading) {
        return <Container><RequestText>로딩 중...</RequestText></Container>;
    }

    return (
        <Container>
            <Title>받은 가족 요청</Title>
            <FlatList
                data={requests}
                renderItem={renderItem}
                keyExtractor={(item, index) => item.requestId ? item.requestId.toString() : index.toString()} // requestId 사용
            />
            <RefreshButton title="새로 고침" onPress={fetchReceivedRequests} />
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
    font-size: 20px;
    font-weight: bold;
    margin-bottom: 10px;
`;

const RequestItem = styled.View`
    padding: 10px;
    border-bottom-width: 1px;
    border-bottom-color: #ccc;
    background-color: white;
    margin-bottom: 5px;
`;

const RequestText = styled.Text`
    font-size: 16px;
`;

const ButtonContainer = styled.View`
    flex-direction: row;
    justify-content: space-between;
    margin-top: 10px;
`;

const ActionButton = styled.TouchableOpacity`
    background-color: #4CAF50; /* 수락 버튼 색상 */
    padding: 10px;
    border-radius: 5px;
    flex: 1;
    margin-right: 5px;
`;

const ButtonText = styled.Text`
    color: white;
    text-align: center;
`;

const RefreshButton = styled.Button`
    margin-top: 10px;
`;
