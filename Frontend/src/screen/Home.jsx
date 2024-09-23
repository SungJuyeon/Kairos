import React, { useEffect, useRef, useState } from "react";
import { Animated, View } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Home() {
    const [isAnimationFinished, setIsAnimationFinished] = useState(false);
    const headImageOpacity = useRef(new Animated.Value(0)).current; // headImage 애니메이션
    const headImage = require('./../../assets/head.png'); // 경로 수정
    const { navigate } = useNavigation();

    useEffect(() => {
        console.log("애니메이션 시작"); // 애니메이션 시작 로그
        // headImage 애니메이션 시작
        Animated.timing(headImageOpacity, {
            toValue: 1,
            duration: 3000,
            useNativeDriver: true,
        }).start(() => {
            console.log("애니메이션 완료"); // 애니메이션 완료 로그
            setIsAnimationFinished(true);
        });
    }, []);

    return (
        <Container>
            <Overlay />
            {!isAnimationFinished && (
            <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
                {/* headImage */}
                <Animated.Image
                    source={headImage}
                    style={{
                        opacity: headImageOpacity,
                        width: 300, // 원하는 크기로 조정
                        height: 300, // 원하는 크기로 조정
                        position: 'absolute',
                        transform: [{ translateX: 0 }, { translateY: 0 }] // 중앙 정렬
                    }}
                />
            </View>
            )}
            {isAnimationFinished && (
                <AnimatedContainer>
                    <Title>Herobot!</Title>
                    <CaptureButtonContainer>
                        <ControlButton onPress={() => navigate('Control')}>
                            <CaptureButtonText>Herobot 제어하기</CaptureButtonText>
                        </ControlButton>
                        <CaptureButtonStyle onPress={() => navigate('SmartHome')}>
                            <CaptureButtonText>Smart Home 제어하기</CaptureButtonText>
                        </CaptureButtonStyle>
                        <RowButtonContainer>
                            <CaptureButtonStyle2 onPress={() => navigate('Chat')}>
                                <CaptureButtonText>가족 채팅방 들어가기</CaptureButtonText>
                            </CaptureButtonStyle2>
                            <CaptureButtonStyle3 onPress={() => navigate('Highlight')}>
                                <CaptureButtonText>하이라이트 보러가기</CaptureButtonText>   
                            </CaptureButtonStyle3>
                        </RowButtonContainer>
                        <CaptureButtonStyle onPress={() => navigate('Tutorial')}>
                            <CaptureButtonText>튜토리얼 하러가기</CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle4 onPress={() => navigate('MyPage')}>
                            <CaptureButtonText3>로그인 / 회원가입</CaptureButtonText3>
                        </CaptureButtonStyle4>
                    </CaptureButtonContainer>
                </AnimatedContainer>
            )}
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

const Overlay = styled.View`
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0);
`;

const AnimatedContainer = styled(Animated.View)`
    flex: 1;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0);
`;

const Title = styled.Text`
    color: white;
    font-size: 50px;
    margin-bottom: 10px;
    font-weight: bold;
`;

const CaptureButtonContainer = styled.View`
    justify-content: center;
    align-items: center;
    margin-top: 20px;
`;

const RowButtonContainer = styled.View`
    flex-direction: row;
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

const CaptureButtonStyle2 = styled.TouchableOpacity`
    background-color: white;
    width: 140px;
    height: 120px;
    border-radius: 10px;
    padding: 20px 20px;
`;

const CaptureButtonStyle3 = styled.TouchableOpacity`
    background-color: #ADCDFF;
    width: 140px;
    height: 120px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-left: 20px;
`;

const CaptureButtonStyle4 = styled.TouchableOpacity`
    background-color: #888888;
    width: 190px;
    height: 60px;
    border-radius: 10px;
    padding: 20px 20px;
    margin-top: 20px;
    margin-right: 110px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 20px;
    font-weight: bold;
`;

const CaptureButtonText2 = styled.Text`
    color: black;
    font-size: 18px;
    font-weight: bold;
`;

const CaptureButtonText3 = styled.Text`
    color: white;
    font-size: 18px;
    font-weight: bold;
`;
