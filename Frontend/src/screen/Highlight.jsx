import React, { useState, useEffect } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, FlatList, Alert } from "react-native";
import styled from 'styled-components/native'
import { useNavigation } from "@react-navigation/native";
import { WebView } from 'react-native-webview';
import axios from 'axios';

export default function Highlight() {
    const { navigate } = useNavigation();
    const [highlights, setHighlights] = useState([]);

    const BASE_URL = 'http://223.194.136.129:8000';

    useEffect(() => {
        fetchHighlights();
    }, []);

    const fetchHighlights = async () => {
        try {
            const response = await axios.get(`${BASE_URL}/highlights`);
            setHighlights(response.data);
        } catch (error) {
            console.error('Error fetching highlights:', error);
            Alert.alert('오류', '하이라이트를 가져오는데 실패했습니다.');
        }
    };

    const renderHighlight = ({ item }) => (
        <HighlightItem>
            <HighlightTitle>{item.title}</HighlightTitle>
            <WebView
                source={{ uri: item.video_url }}
                style={{ width: '100%', height: 200 }}
            />
        </HighlightItem>
    );

    return (
        <Container>
            <Title>Herobot이 만든 하이라이트 영상</Title>
            <FlatList
                data={highlights}
                renderItem={renderHighlight}
                keyExtractor={(item) => item.id.toString()}
            />
            <Button onPress={() => navigate("Emotion")}>
                <ButtonText>감정 보러가기</ButtonText>
            </Button>
        </Container>
    );
}

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    padding: 20px;
`;

const Title = styled.Text`
    color: white;
    font-size: 24px;
    margin-bottom: 20px;
    font-weight: bold;
`;

const HighlightItem = styled.View`
    margin-bottom: 20px;
`;

const HighlightTitle = styled.Text`
    color: white;
    font-size: 18px;
    margin-bottom: 10px;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFB0F9;
    padding: 10px 20px;
    border-radius: 5px;
    align-self: center;
    margin-top: 20px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 16px;
    font-weight: bold;
`;