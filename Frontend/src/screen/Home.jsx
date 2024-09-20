import React, { useEffect, useRef, useState } from "react";
import { ImageBackground, Animated, View } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Home() {
    const ball1Y = useRef(new Animated.Value(-100)).current;
    const ball2Y = useRef(new Animated.Value(-100)).current;
    const [isAnimationFinished, setIsAnimationFinished] = useState(false);
    const fadeInOpacity = useRef(new Animated.Value(0)).current;
    const welcomeOpacity = useRef(new Animated.Value(0)).current; // 추가된 코드
    const welcomeTranslateX = useRef(new Animated.Value(-100)).current; // 추가된 코드
    const backgroundImage = { uri: 'https://images.unsplash.com/photo-1541873676-a18131494184?w=900&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxleHBsb3JlLWZlZWR8NHx8fGVufDB8fHx8fA%3D%3D' };
    const { navigate } = useNavigation();
    const circleOpacity = useRef(new Animated.Value(0)).current;
    const circleOpacity2 = useRef(new Animated.Value(0)).current;
    const circleOpacity3 = useRef(new Animated.Value(0)).current;
    const circleOpacity4 = useRef(new Animated.Value(0)).current;


    useEffect(() => {
        Animated.parallel([
            Animated.timing(ball1Y, {
                toValue: 290,
                duration: 2500,
                useNativeDriver: true,
            }),
            Animated.timing(ball2Y, {
                toValue: 290,
                duration: 2500,
                useNativeDriver: true,
            }),
            Animated.timing(circleOpacity, {
                toValue: 1,
                duration: 3000,
                useNativeDriver: true,
            }),
            Animated.timing(circleOpacity2, {
                toValue: 1,
                duration: 3000,
                useNativeDriver: true,
            }),
            Animated.timing(circleOpacity3, {
                toValue: 1,
                duration: 3000,
                useNativeDriver: true,
            }),
            Animated.timing(circleOpacity4, {
                toValue: 1,
                duration: 3000,
                useNativeDriver: true,
            }),
            // 추가된 애니메이션
            Animated.parallel([
                Animated.timing(welcomeOpacity, {
                    toValue: 1,
                    duration: 5000,
                    useNativeDriver: true,
                }),
                Animated.timing(welcomeTranslateX, {
                    toValue: 0,
                    duration: 2000,
                    useNativeDriver: true,
                }),
            ]),
        ]).start(() => {
            setIsAnimationFinished(true);
            Animated.timing(fadeInOpacity, {
                toValue: 1,
                duration: 1000,
                useNativeDriver: true,
            }).start();
        });
    }, []);

    return (
        <Container>
            <Overlay />
            {!isAnimationFinished && (
                <View style={{ flex: 1, justifyContent: 'flex-start', alignItems: 'center' }}>
                    <AnimatedBall style={{ transform: [{ translateY: ball1Y }, { translateX: -60 }], zIndex: 2 }} />
                    <AnimatedBall style={{ transform: [{ translateY: ball2Y }, { translateX: 60 }], zIndex: 2 }} />
                    <AnimatedCircle style={{ opacity: circleOpacity, top: '40%', left: '37%', transform: [{ translateX: -75 }, { translateY: -75 }], zIndex: 1 }} />
                    <AnimatedCircle2 style={{ opacity: circleOpacity2, top: '56%', left: '56%', transform: [{ translateX: -75 }, { translateY: -75 }], zIndex: 1 }} />
                    <AnimatedCircle3 style={{ opacity: circleOpacity3, top: '36%', left: '40%', transform: [{ translateX: -75 }, { translateY: -75 }], zIndex: 1 }} />
                    <AnimatedCircle3 style={{ opacity: circleOpacity3, top: '36%', left: '65%', transform: [{ translateX: -75 }, { translateY: -75 }], zIndex: 1 }} />
                    <AnimatedCircle4 style={{ opacity: circleOpacity4, top: '70%', left: '56%', transform: [{ translateX: -75 }, { translateY: -75 }], zIndex: 1 }} />
                    {/* 추가된 welcome 텍스트 */}
                    <AnimatedWelcome style={{
                        opacity: welcomeOpacity,
                        transform: [{ translateX: welcomeTranslateX }],
                        zIndex: 3,
                        position: 'absolute',
                        top: 550, // 위치 조정
                        fontSize: 50,
                    }}>
                        welcome!
                    </AnimatedWelcome>
                </View>
            )}
            {isAnimationFinished && (
                <AnimatedContainer style={{ opacity: fadeInOpacity }}>
                    <Title>Herobot!</Title>
                    <CaptureButtonContainer>
                        <ControlButton onPress={() => navigate('Control')}>
                            <CaptureButtonText>Herobot 제어하기</CaptureButtonText>
                        </ControlButton>
                        <CaptureButtonStyle onPress={() => navigate('SmartHome')}>
                            <CaptureButtonText>Smart Home 제어하기</CaptureButtonText>
                        </CaptureButtonStyle>
                        <CaptureButtonStyle onPress={() => navigate('MyPage')}>
                            <CaptureButtonText>로그인 / 회원가입</CaptureButtonText>
                        </CaptureButtonStyle>
                    </CaptureButtonContainer>
                </AnimatedContainer>
            )}
        </Container>
    );
}

// 추가된 스타일
const AnimatedWelcome = styled(Animated.Text)`
    color: white;
    font-size: 24px;
    font-weight: bold;
`;

const Title = styled.Text`
    color: white;
    font-size: 50px;
    margin-bottom: 10px;
    font-weight: bold;
`;

const AnimatedContainer = styled(Animated.View)`
    flex: 1;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0);
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
    font-size: 18px;
    font-weight: bold;
`;

const Overlay = styled.View`
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0);
`;

const AnimatedBall = styled(Animated.View)`
    width: 50px;
    height: 50px;
    border-radius: 25px; 
    background-color: #000000; 
    position: absolute;
`;

const AnimatedCircle = styled(Animated.View)`
    width: 300px;
    height: 300px;
    border-radius: 150px;
    background-color: #FFFFFF;
    position: absolute;
`;

const AnimatedCircle2 = styled(Animated.View)`
    width: 80px;
    height: 80px;
    border-radius: 40px;
    background-color: #000000;
    position: absolute;
`;

const AnimatedCircle3 = styled(Animated.View)`
    width: 120px;
    height: 120px;
    border-radius: 30px;
    background-color: #FFFFFF;
    position: absolute;
    transform: rotate(45deg);
`;

const AnimatedCircle4 = styled(Animated.View)`
    width: 80px;
    height: 20px;
    border-radius: 10px;
    background-color: #000000;
    position: absolute;
    transform: rotate(45deg);
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: center;
    align-items: center;
`;