import React, { useState, useEffect } from "react";
import { Alert, Platform, Dimensions, Text } from "react-native";
import styled from 'styled-components/native';
import * as FileSystem from 'expo-file-system';
import Slider from '@react-native-community/slider';
import * as ImagePicker from 'expo-image-picker';
import { WebView } from 'react-native-webview';
import * as MediaLibrary from 'expo-media-library';

// 스타일 컴포넌트를 위함
const { width, height } = Dimensions.get('window');

const BASE_URL = 'http://10.0.2.2:8000';
const imageURL = `${BASE_URL}/video`;

// 비율에 따른 스타일 조정
const scale = width / 640; // 기준 너비에 대한 비율

export default function Control() {
    const [isForwardPressed, setIsForwardPressed] = useState(false);
    const [isLeftPressed, setIsLeftPressed] = useState(false);
    const [isRightPressed, setIsRightPressed] = useState(false);
    const [isBackPressed, setIsBackPressed] = useState(false);
    const [isStopPressed, setIsStopPressed] = useState(false);
    const [isUpPressed, setIsUpPressed] = useState(false);
    const [isDownPressed, setIsDownPressed] = useState(false);
    const [isOn, setIsOn] = useState(false);
    const [isFace, setIsFace] = useState(false);
    const [isGesture, setIsGesture] = useState(false);

    const webViewRef = React.useRef(null);
    const [value, setValue] = useState(5);

    // 방향키 버튼을 누르고 있을 때
    const handleButtonPressIn = async (direction) => {
        switch (direction) {
            case 'forward':
                setIsForwardPressed(true);
                await fetch(`${BASE_URL}/move/forward`, { method: 'POST' });
                break;
            case 'left':
                setIsLeftPressed(true);
                await fetch(`${BASE_URL}/move/left`, { method: 'POST' });
                break;
            case 'right':
                setIsRightPressed(true);
                await fetch(`${BASE_URL}/move/right`, { method: 'POST' });
                break;
            case 'back':
                setIsBackPressed(true);
                await fetch(`${BASE_URL}/move/back`, { method: 'POST' });
                break;
            case 'stop':
                setIsStopPressed(true);
                await fetch(`${BASE_URL}/stop`, { method: 'POST' });
                await fetch(`${BASE_URL}/move/stop_actuator`, { method: 'POST' });
                break;
            case 'up':
                setIsUpPressed(true);
                await fetch(`${BASE_URL}/move/up`, { method: 'POST' });
                break;
            case 'down':
                setIsUpPressed(true);
                await fetch(`${BASE_URL}/move/down`, { method: 'POST' });
                break;
        }
    };

    // 방향키 버튼을 누르다가 땔 때
    const handleButtonPressOut = async (direction) => {
        switch (direction) {
            case 'forward':
                setIsForwardPressed(false);
                break;
            case 'left':
                setIsLeftPressed(false);
                break;
            case 'right':
                setIsRightPressed(false);
                break;
            case 'back':
                setIsBackPressed(false);
                break;
            case 'up':
                setIsUpPressed(true);
                break;
            case 'down':
                setIsDownPressed(true);
                break;
        }
        // 모터 정지 요청
        await fetch(`${BASE_URL}/stop`, { method: 'POST' });
        await fetch(`${BASE_URL}/move/stop_actuator`, { method: 'POST' });
        setIsStopPressed(true);
    };

    // 웹뷰 캡쳐 함수
    useEffect(() => {
        const requestPermission = async () => {
            const { status } = await MediaLibrary.requestPermissionsAsync();
            if (status !== 'granted') {
                Alert.alert('Permission needed', 'This app needs access to your photo library.');
            }
        };
        requestPermission();
    }, []);

    const handleCapturePhoto = async () => {
        if (webViewRef.current) {
            console.log('Capturing photo from WebView...');
            webViewRef.current.injectJavaScript(`
                (function() {
                    const img = document.querySelector('img'); // 캡처할 이미지 선택
                    if (img) {
                        const canvas = document.createElement('canvas');
                        canvas.width = img.width;
                        canvas.height = img.height;
                        const ctx = canvas.getContext('2d');
                        ctx.drawImage(img, 0, 0);
                        const dataURL = canvas.toDataURL('image/jpeg');
                        window.ReactNativeWebView.postMessage(dataURL);
                    }
                })();
            `);
        }
    };

    const onMessage = async (event) => {
        const base64Data = event.nativeEvent.data;
        try {
            const base64Image = base64Data.split(',')[1];
            const fileUri = FileSystem.documentDirectory + 'image.jpg';
            await FileSystem.writeAsStringAsync(fileUri, base64Image, {
                encoding: FileSystem.EncodingType.Base64,
            });
            const asset = await MediaLibrary.createAssetAsync(fileUri);
            Alert.alert('사진 찍기 완료', '사진이 갤러리에 저장되었습니다.');
        } catch (error) {
            Alert.alert('사진 찍기 실패', '오류가 발생했습니다.');
        }
    };

    // 속도 조절 코드
    const handleValueChange = async (newValue) => {
        setValue(newValue);
        await fetch(`/speed/${newValue * 10}`, { method: 'POST' });
    };

    // 갤러리 열기
    const openGallery = async () => {
        const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (permissionResult.granted === false) {
            alert('사진 접근 권한이 필요합니다!');
            return;
        }
        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.All,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 1,
        });

        if (!result.canceled) {
            setImage(result.assets[0].uri);
        }
    };

    // Face 버튼 클릭 핸들러
    const toggleFace = () => {
        setIsFace(prev => !prev);
    };

    // Gesture 버튼 클릭 핸들러
    const toggleGesture = () => {
        setIsGesture(prev => !prev);
    };

    return (
        <Container>
            <MarginContainer />
            <ImageContainer>
                {Platform.OS === 'web' ? (
                    <img src={imageURL} width="100%" alt="Live Stream" />
                ) : (
                    <StyledWebView
                        source={{ uri: `${BASE_URL}/video_feed/${isFace}` }}
                        ref={webViewRef}
                        onMessage={onMessage}
                    />
                )}
            </ImageContainer>

            <Margin2Container />

            <BorderContainer />

                <CaptureButtonContainer>
                    <CaptureButtonStyle onPress={handleCapturePhoto}>
                        <CaptureButtonText>Picture</CaptureButtonText>
                    </CaptureButtonStyle>
                    <CaptureButtonStyle onPress={openGallery}>
                        <CaptureButtonText>Gallery</CaptureButtonText>
                    </CaptureButtonStyle>
                    <RemoveContainer>
                        <OnOffButton onPress={toggleFace} isOn={isFace}>
                            <OnOffButtonText isOn={isFace}>{isFace ? 'Face' : 'Face'}</OnOffButtonText>
                        </OnOffButton>
                        <OnOffButton onPress={toggleGesture} isOn={isGesture}>
                            <OnOffButtonText isOn={isGesture}>{isGesture ? 'Gesture' : 'Gesture'}</OnOffButtonText>
                        </OnOffButton>
                    </RemoveContainer>
                </CaptureButtonContainer>

                <ControlPadContainer>
                    <SpeedSliderContainer>
                        <SliderTextContainer>
                            <SliderText>Speed</SliderText>
                            <SliderText>     {value}</SliderText>
                        </SliderTextContainer>
                        <StyledSlider
                            minimumValue={0}
                            maximumValue={10}
                            step={1}
                            value={value}
                            onValueChange={handleValueChange}
                            minimumTrackTintColor="#FFCEFF"
                            maximumTrackTintColor="#555555"
                            thumbTintColor="#FFCEFF"
                        />
                    </SpeedSliderContainer>

                    <ButtonContainer>
                        <DirectionButtonContainer>
                            <CamButton
                                onPressIn={() => handleButtonPressIn('up')}
                                onPressOut={() => handleButtonPressOut('up')}
                            >
                                <CamButtonText>{isUpPressed ? 'Up' : 'Up'}</CamButtonText>
                            </CamButton>
                            <ButtonStyle3
                                onPressIn={() => handleButtonPressIn('forward')}
                                onPressOut={() => handleButtonPressOut('forward')}
                            >
                                <ButtonText>{isForwardPressed ? '▲' : '▲'}</ButtonText>
                            </ButtonStyle3>
                            <CamButton2
                                onPressIn={() => handleButtonPressIn('down')}
                                onPressOut={() => handleButtonPressOut('down')}
                            >
                                <CamButtonText>{isDownPressed ? 'Down' : 'Down'}</CamButtonText>
                            </CamButton2>
                        </DirectionButtonContainer>
                        <DirectionButtonContainer2>
                            <ButtonStyle2
                                onPressIn={() => handleButtonPressIn('left')}
                                onPressOut={() => handleButtonPressOut('left')}
                            >
                                <ButtonText>{isLeftPressed ? '◀' : '◀'}</ButtonText>
                            </ButtonStyle2>
                            <ButtonStyle3
                                onPressIn={() => handleButtonPressIn('stop')}
                                onPressOut={() => handleButtonPressOut('stop')}
                            >
                                <ButtonText>{isStopPressed ? '●' : '●'}</ButtonText>
                            </ButtonStyle3>
                            <ButtonStyle3
                                onPressIn={() => handleButtonPressIn('right')}
                                onPressOut={() => handleButtonPressOut('right')}
                            >
                                <ButtonText>{isRightPressed ? '▶' : '▶'}</ButtonText>
                            </ButtonStyle3>
                        </DirectionButtonContainer2>
                        <DownButtonContainer>
                            <ButtonStyle
                                onPressIn={() => handleButtonPressIn('back')}
                                onPressOut={() => handleButtonPressOut('back')}
                            >
                                <ButtonText>{isBackPressed ? '▼' : '▼'}</ButtonText>
                            </ButtonStyle>
                        </DownButtonContainer>
                    </ButtonContainer>        
                </ControlPadContainer>
            <BorderContainer />
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 50px;
    margin-bottom: 20px;
    font-weight: bold;
`;

const StyledText = styled.Text`
    color: white; 
    font-size: 18px;
    font-weight: bold;
`;

const RemoveContainer = styled.View`
    flex-direction: row;
    align-items: center;
    margin-left: 10px;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const MarginContainer = styled.View`
    margin-top: 9%;
`;

const Margin2Container = styled.View`
    margin-top: 2%;
`;

const BorderContainer = styled.View`
    border: 3px solid #ADCDFF;
    width: ${width * 0.90}px;
    margin: 2%;
`;

const ButtonContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
`;

const UpButtonContainer = styled.View`
    margin-top: 20px;
    margin-bottom: 20px;
    margin-left: 100px;
`;

const DirectionButtonContainer = styled.View`
    flex-direction: row;
    margin-top: 20px;
    margin-bottom: 20px;
    width: 200px;

`;

const DirectionButtonContainer2 = styled.View`
    flex-direction: row;
    margin-bottom: 20px;
    width: 200px;

`;

const DownButtonContainer = styled.View`
    margin-top: 0px;
    margin-left: 100px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 20px; 
    font-weight: bold;
`;

const CamButtonText = styled.Text`
    color: black;
    font-size: 15px; 
    font-weight: bold;
`;

const CaptureButtonContainer = styled.View`
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top: 10px;
    margin-bottom: 10px;
`;

const ControlPadContainer = styled.View`
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top: 10px;
    margin-bottom: 10px;
`;

const SpeedSliderContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: absolute;
    right: 180px;
    bottom: 50px;
    padding: 5px;
    border-radius: 10px;
    padding: 10px;
    z-index: 10;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 12px; 
    font-weight: bold;
`;

const OnOffButton = styled.TouchableOpacity`
    width: 70px; 
    height: 45px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isOn }) => (isOn ? '#ADCDFF' : '#AAAAAA')};
    border-radius: 10px;
    padding: 10px 10px;
    margin-left: 15px;
`;

const OnOffButtonText = styled.Text`
    color: black;
    font-size: 12px;
    font-weight: bold;
`;

const CamButton = styled.TouchableOpacity`
    background-color: #ADCDFF;
    border-radius: 10px;
    padding: 10px 10px;
    width: 65px;
    height: ${scale * 90}px;
    justify-content: center;
    align-items: center;
    margin-left: 30px;
`;

const CamButton2 = styled.TouchableOpacity`
    background-color: #ADCDFF;
    border-radius: 10px;
    padding: 10px 10px;
    width: 65px;
    height: 55px;
    justify-content: center;
    align-items: center;
    margin-left: 20px;
`;

const ButtonStyle = styled.TouchableOpacity`
    background-color: white;
    border-radius: 10px;
    padding: 10px 10px;
    margin: 0 40px;
    width: 65px;
    height: 55px;
    justify-content: center;
    align-items: center;
`;

const ButtonStyle2 = styled.TouchableOpacity`
    background-color: white;
    border-radius: 10px;
    padding: 10px 10px;
    width: 65px;
    height: 55px;
    justify-content: center;
    align-items: center;
    margin-left: 30px;
`;

const ButtonStyle3 = styled.TouchableOpacity`
    background-color: white;
    border-radius: 10px;
    padding: 10px 10px;
    width: 65px;
    height: 55px;
    justify-content: center;
    align-items: center;
    margin-left: 20px;
`;

const StopButton = styled.TouchableOpacity`
    background-color: white;
    border-radius: 10px;
    padding: 10px 10px;
    width: 100px;
    height: 80px;
    justify-content: center;
    align-items: center;
    margin-left: 20px;
`;

const CaptureButtonStyle = styled.TouchableOpacity`
    width: 80px; 
    height: 45px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isCaptureVideoPressed }) => (isCaptureVideoPressed ? '#AAAAAA' : '#FFCEFF')};
    border-radius: 10px;
    padding: 10px 10px;
    margin: 0 8px;
`;

const ImageContainer = styled.View`
    width: 90%;
    height: 34%;
    border-width: 2px; 
    border-color: #FFCEFF;
    background-color: #222222; 
`;

const StyledImage = styled.Image`
    width: 100%;
    height: 100%;
`;

const SliderTextContainer = styled.View`
    background-color: #FFFFFF;
    border-radius: 10px;
    margin-bottom: 60px;
    padding: 7px;
`;

const SliderText = styled.Text`
    font-size: 18px;
    color: black;
    font-weight: bold;
`;

const StyledSlider = styled(Slider)`
    width: 150px;
    transform: rotate(-90deg);
`;

const StyledWebView = styled(WebView)`
  flex: 1;
`;
