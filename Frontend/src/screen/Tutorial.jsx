import React, { useEffect, useRef, useState } from "react";
import { Animated, ScrollView } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Tutorial() {
    const { navigate } = useNavigation();

    return (
        <Container>
            <AnimatedContainer>
                <Title>튜토리얼에 오신 것을 환영합니다.</Title>
                <ScrollView 
                    contentContainerStyle={{ alignItems: 'center' }} 
                    showsVerticalScrollIndicator={false} // 스크롤바 숨기기
                >
                    <CaptureButtonContainer>
                        <CaptureButtonStyle onPress={() => navigate('Function1')}>
                            <CaptureButtonText>1. </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function2')}>
                            <CaptureButtonText>2.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function3')}>
                            <CaptureButtonText>3.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function4')}>
                            <CaptureButtonText>4.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function5')}>
                            <CaptureButtonText>5.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function6')}>
                            <CaptureButtonText>6.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function7')}>
                            <CaptureButtonText>7.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function8')}>
                            <CaptureButtonText>8.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function9')}>
                            <CaptureButtonText>9.  </CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('Function10')}>
                            <CaptureButtonText>10.  </CaptureButtonText>
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
    margin-bottom: 10px;
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
