import { FA5Style } from '@expo/vector-icons/build/FontAwesome5';
import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, ScrollView, TouchableOpacity, Alert } from 'react-native';
import styled from 'styled-components/native';

export default function Repository() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('https://jsonplaceholder.typicode.com/posts');
        if (!response.ok) {
          throw new Error('네트워크 응답이 좋지 않습니다.');
        }
        const json = await response.json();
        setData(json);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleButtonPress = (item) => {
    Alert.alert(`아이템 선택: ${item.title}`);
    // 여기에 원하는 작업을 추가할 수 있습니다.
  };

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text>{error}</Text>;
  }

  return (
    <Container>
      <Title>하이라이트 저장소</Title>
      <ScrollView
        style={{ flex: 1 }}
        showsVerticalScrollIndicator={false}
      >
        {data.map(item => (
          <Item key={item.id}>
            <ItemTitle>{item.title}</ItemTitle>
            <ItemText>{item.body}</ItemText>
            <Button onPress={() => handleButtonPress(item)}>
              <ButtonText>다운로드</ButtonText>
            </Button>
          </Item>
        ))}
      </ScrollView>
    </Container>
  );
};

const Title = styled.Text`
  color: white;
  font-size: 35px;
  margin-top: 10px;
  margin-bottom: 10px;
  font-weight: bold;
`;

const Container = styled.SafeAreaView`
  background-color: #1B0C5D;
  flex: 1;
  justify-content: center;
  align-items: center;
`;

const Item = styled.View`
  padding: 20px;
  border-bottom-width: 1px;
  border-bottom-color: #ccc;
`;

const ItemTitle = styled.Text`
  color: #FFFFFF;
  font-weight: bold;
  font-size: 16px;
`;

const ItemText = styled.Text`
  color: #FFFFFF;
`;

const Button = styled(TouchableOpacity)`
  background-color: #FFFFFF;
  padding: 10px;
  border-radius: 5px;
  margin-top: 10px;
  align-items: center;
`;

const ButtonText = styled.Text`
  color: black;
  font-weight: bold;
`;
