import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, ScrollView, TouchableOpacity, Alert } from 'react-native';
import styled from 'styled-components/native';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';

export default function Repository() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('데이터 로딩 시작...');
        const response = await fetch('http://localhost:8000/s3_video_list');
        if (!response.ok) {
          throw new Error('네트워크 응답이 좋지 않습니다.');
        }
        const json = await response.json();
        console.log('데이터 로딩 완료:', json.videos);
        setData(json.videos);
      } catch (error) {
        console.error('데이터 로딩 중 오류 발생:', error.message);
        setError(error.message);
      } finally {
        setLoading(false);
        console.log('로딩 상태 업데이트:', loading);
      }
    };

    fetchData();
  }, []);

  const handleButtonPress = async (item) => {
    console.log(`다운로드 버튼 클릭: ${item.file_name}`);

    if (!item.file_name) {
      Alert.alert('다운로드 실패', '유효한 비디오 URL이 없습니다.');
      return;
    }

    const downloadPath = FileSystem.documentDirectory + item.file_name;

    try {
      console.log(`다운로드 시작: ${item.video_url}`);
      const { uri } = await FileSystem.downloadAsync(item.video_url, downloadPath);
      console.log(`다운로드 완료: ${uri}`);

      // 갤러리에 저장
      const asset = await MediaLibrary.createAssetAsync(uri);
      await MediaLibrary.createAlbumAsync('My Videos', asset, false);
      Alert.alert('다운로드 완료', `${item.file_name}이 갤러리에 저장되었습니다.`);
    } catch (error) {
      console.error('다운로드 중 오류 발생:', error.message);
      Alert.alert('다운로드 실패', error.message);
    }
  };

  if (loading) {
    console.log('로딩 중...');
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    console.error('에러 상태:', error);
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
