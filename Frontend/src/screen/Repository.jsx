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
        const response = await fetch('http://localhost:8000/s3_video_list'); // S3 비디오 목록 API 호출
        if (!response.ok) {
          throw new Error('네트워크 응답이 좋지 않습니다.');
        }
        const json = await response.json();
        setData(json.videos); // 비디오 목록 데이터를 설정
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleButtonPress = (item) => {
    Alert.alert(`아이템 선택: ${item.file_name}`);
    // 여기에 다운로드 로직 등을 추가할 수 있습니다.
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
          <Item key={item.file_name}>
            <ItemTitle>{item.person_name}의 {item.emotion}</ItemTitle>
            <ItemText>{item.date_time}</ItemText>
            <Thumbnail source={{ uri: item.thumbnail_url }} />
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
  background-color: #222222;
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

const Thumbnail = styled.Image`
  width: 100%;
  height: 75px;
  margin-top: 10px;
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
