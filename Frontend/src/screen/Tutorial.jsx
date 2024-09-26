import React, { useEffect, useRef, useState } from "react";
import { Animated, ScrollView } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Tutorial() {
    const { navigate } = useNavigation();

    return (
        <Container>
            <AnimatedContainer>
                <Title>히어로봇 알아가기</Title>
                <ScrollView 
                    contentContainerStyle={{ alignItems: 'center' }} 
                    showsVerticalScrollIndicator={false} // 스크롤바 숨기기
                >
                    <CaptureButtonContainer>
                        <CaptureButtonStyle onPress={() => navigate('Function1')}>
                            <CaptureButtonText>1. 히어로봇의 거리 전송 기능 </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function2')}>
                            <CaptureButtonText>2. 히어로봇의 영상 전송 기능 </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function3')}>
                            <CaptureButtonText>3. 히어로봇의 음성 감지 기능 </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function4')}>
                            <CaptureButtonText>4. 히어로봇의 따라오기 기능 </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function5')}>
                            <CaptureButtonText>5. 히어로봇의 감정 인식 기능 </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function6')}>
                            <CaptureButtonText>6. 히어로봇의 손동작 인식 기능 </CaptureButtonText>
                        </CaptureButtonStyle>
                    </CaptureButtonContainer>
                </ScrollView>
            </AnimatedContainer>
        </Container>
    );
}

// 나머지 스타일 코드
const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const AnimatedContainer = styled(Animated.View)`
    flex: 1;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0);
`;

const Title = styled.Text`
    color: white;
    font-size: 25px;
    margin-top: 20px;
    font-weight: bold;
`;

const CaptureButtonContainer = styled.View`
    justify-content: center;
    align-items: center;
    margin-top: 20px;
`;

const ControlButton = styled.TouchableOpacity`
    background-color: #FFCEFF;
    width: 300px;
    height: 60px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-top: 20px;
`;

const CaptureButtonStyle = styled.TouchableOpacity`
    background-color: white;
    width: 300px;
    height: 60px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-top: 20px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 20px;
    font-weight: bold;
`;
