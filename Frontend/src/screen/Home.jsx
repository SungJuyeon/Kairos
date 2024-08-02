import React, { useEffect, useRef, useState } from "react";
import { ImageBackground, Animated } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

export default function Home() {
    const opacity = useRef(new Animated.Value(0)).current; // 초기값 0, 인트로 애니메이션을 위함
    const contentOpacity = useRef(new Animated.Value(0)).current; // 나머지 UI의 초기값
    const [isAnimationFinished, setIsAnimationFinished] = useState(false); // 애니메이션 완료 상태
    const backgroundImage = { uri: '../assets/Home.jpg' };
    const { navigate } = useNavigation();

    useEffect(() => {
        // 첫 번째 애니메이션 실행
        Animated.timing(opacity, {
            toValue: 1, // 최종값
            duration: 2000, // 애니메이션 지속 시간
            useNativeDriver: true, // 네이티브 드라이버 사용
        }).start(() => {
            setIsAnimationFinished(true); // 애니메이션이 끝나면 상태 업데이트
            
            // 두 번째 애니메이션 실행
            Animated.timing(contentOpacity, {
                toValue: 1, // 최종값
                duration: 1000, // 애니메이션 지속 시간
                useNativeDriver: true, // 네이티브 드라이버 사용
            }).start();
        });
    }, [opacity]);

    return (
        <ImageBackground source={backgroundImage} style={{ flex: 1 }} resizeMode="cover">
            {!isAnimationFinished && ( // 애니메이션이 끝나지 않았을 때만 표시
                <AnimatedContainer style={{ opacity }}>
                    <WelcomeText>Hello</WelcomeText>
                    <WelcomeText>Herobot!</WelcomeText>
                </AnimatedContainer>
            )}
            {isAnimationFinished && ( // 애니메이션이 끝난 후 나머지 UI 표시
                    <Container style={{ opacity: contentOpacity }}>
                        <Title>Welcome!</Title>
                        <CaptureButtonContainer>
                            <CaptureButtonStyle onPress={() => navigate('Control')}>
                                <CaptureButtonText>Herobot 제어하기</CaptureButtonText>
                            </CaptureButtonStyle>
                            <CaptureButtonStyle>
                                <CaptureButtonText>Smart Home 제어하기</CaptureButtonText>
                            </CaptureButtonStyle>
                        </CaptureButtonContainer>
                    </Container>
            )}
        </ImageBackground>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 50px;
    margin-bottom: 10px;
    font-weight: bold;
`;

const Container = styled.View`
    flex: 1;
    justify-content: center;
    align-items: center;
    background-color: rgba(0, 0, 0, 0.5);
`;

const CaptureButtonContainer = styled.View`
    justify-content: center;
    align-items: center;
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

const AnimatedContainer = styled(Animated.View)`
  flex: 1;
  justify-content: center;
  align-items: center;
`;

const WelcomeText = styled.Text`
  font-size: 54px;
  font-weight: bold;
  color: white;
  margin-bottom: 20px;
`;
