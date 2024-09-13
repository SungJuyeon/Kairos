import React, { useState, useEffect } from "react";
import { Alert, Platform, Dimensions, Text } from "react-native";
import styled from 'styled-components/native';
import * as FileSystem from 'expo-file-system';
import Slider from '@react-native-community/slider';
import * as ImagePicker from 'expo-image-picker';
import { WebView } from 'react-native-webview'
import * as MediaLibrary from 'expo-media-library';


    // 스타일 컴포넌트를 위함
    const { width, height } = Dimensions.get('window');

    // 비율에 따른 스타일 조정
    const scale = width / 640; // 기준 너비에 대한 비율


export default function Control() {
    const [isUpPressed, setIsUpPressed] = useState(false);
    const [isLeftPressed, setIsLeftPressed] = useState(false);
    const [isRightPressed, setIsRightPressed] = useState(false);
    const [isDownPressed, setIsDownPressed] = useState(false);
    const [isCaptureVideoPressed, setIsCaptureVideoPressed] = useState(false);
    const [isOn, setIsOn] = useState(false); // on/off 상태 추가

    // 웹뷰 캡쳐
    const webViewRef = React.useRef(null);

    // 속도 조절
    const [value, setValue] = useState(5);

    const BASE_URL = 'http://localhost:8000';
    const imageURL = `${BASE_URL}/video`;

    // 안드로이드에서 사진 저장 권한을 위한 함수
    // const requestCameraRollPermission = async () => {
    //     try {
    //         const granted = await PermissionsAndroid.request(
    //             PermissionsAndroid.PERMISSIONS.WRITE_EXTERNAL_STORAGE,
    //             {
    //                 title: '저장 권한 요청',
    //                 message: '앱이 갤러리에 사진을 저장할 수 있도록 권한을 요청합니다.',
    //                 buttonNeutral: '나중에',
    //                 buttonNegative: '취소',
    //                 buttonPositive: '확인',
    //             }
    //         );
    //         return granted === PermissionsAndroid.RESULTS.GRANTED;
    //     } catch (err) {
    //         console.warn(err);
    //         return false;
    //     }
    // };

    // 방향키 버튼을 누르고 있을 때
    const handleButtonPressIn = async (direction) => {
        switch (direction) {
            case 'up':
                setIsUpPressed(true);
                await fetch(`${BASE_URL}/move/up`, { method: 'POST' });
                break;
            case 'left':
                setIsLeftPressed(true);
                await fetch(`${BASE_URL}/move/left`, { method: 'POST' });
                break;
            case 'right':
                setIsRightPressed(true);
                await fetch(`${BASE_URL}/move/right`, { method: 'POST' });
                break;
            case 'down':
                setIsDownPressed(true);
                await fetch(`${BASE_URL}/move/down`, { method: 'POST' });
                break;
        }
    };


    // 방향키 버튼을 누르다가 땔 때
    const handleButtonPressOut = async (direction) => {
        switch (direction) {
            case 'up':
                setIsUpPressed(false);
                break;
            case 'left':
                setIsLeftPressed(false);
                break;
            case 'right':
                setIsRightPressed(false);
                break;
            case 'down':
                setIsDownPressed(false);
                break;
        }
        // 모터 정지 요청
        await fetch(`${BASE_URL}/stop`, { method: 'POST' });
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
                    console.log('Image found in WebView'); // 이미지 발견 로그
                    const canvas = document.createElement('canvas');
                    canvas.width = img.width;
                    canvas.height = img.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0);
                    const dataURL = canvas.toDataURL('image/jpeg');
                    console.log('Image captured as dataURL:', dataURL); // 데이터 URL 캡처 로그
                    window.ReactNativeWebView.postMessage(dataURL);
                } else {
                    console.log('No image found in WebView'); // 이미지 미발견 로그
                }
            })();
        `);
    }
};

const onMessage = async (event) => {
    const base64Data = event.nativeEvent.data;
    console.log('Received data from WebView', base64Data.length); // 데이터 수신 로그 및 길이
    try {
        console.log('Saving image to photo library...');
        // Base64 데이터에서 메타데이터 제거
        const base64Image = base64Data.split(',')[1]; // 'data:image/jpeg;base64,' 부분을 제거
        
        // 임시 파일 경로 생성
        const fileUri = FileSystem.documentDirectory + 'image.jpg';
        
        // Base64 데이터를 파일로 저장
        await FileSystem.writeAsStringAsync(fileUri, base64Image, {
            encoding: FileSystem.EncodingType.Base64,
        });

        // MediaLibrary에 저장
        const asset = await MediaLibrary.createAssetAsync(fileUri);
        console.log('Image saved to photo library successfully:', asset); // 저장 성공 로그
        Alert.alert('사진 찍기 완료', '사진이 갤러리에 저장되었습니다.');
    } catch (error) {
        console.error('Error saving image:', error); // 에러 로그
        Alert.alert('사진 찍기 실패', '오류가 발생했습니다.');
    }
};



    // 속도 조절 코드
    const handleValueChange = async (newValue) => {
        setValue(newValue); // 새로운 값으로 업데이트


        // 서버에 fetch 요청
        await fetch(`http://localhost:8000/speed/${newValue > value ? 'up' : 'down'}`, { method: 'POST' });
        
    };



    // 갤러리 열기

    const openGallery = async () => {
    // 권한 요청
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (permissionResult.granted === false) {
        alert('사진 접근 권한이 필요합니다!');
        return;
    }

    // 갤러리 열기
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
    


    return (
        <Container>

            <MarginContainer />

            <ImageContainer>
                {Platform.OS === 'web' ? (
                     <img src={imageURL} width="100%" alt="Live Stream" />
                ) : (
                    <StyledWebView
                        source={{ uri: imageURL }}
                        ref={webViewRef}
                        onMessage={onMessage}
                    />
                )}
            </ImageContainer>

            <Margin2Container />
            <BorderContainer></BorderContainer>

            <Border2Container>

            <CaptureButtonContainer>
                <CaptureButtonStyle
                    onPress={() => handleCapturePhoto(webViewRef)}>
                    <CaptureButtonText>Picture</CaptureButtonText>
                </CaptureButtonStyle>
                <RemoveContainer>
                    <StyledText>__________</StyledText>
                    <OnOffButton
                        onPress={openGallery}
                        isOn={isOn}>
                        <OnOffButtonText isOn={isOn}>{isOn ? 'Gallery' : 'Gallery'}</OnOffButtonText>
                    </OnOffButton>
                </RemoveContainer>
            </CaptureButtonContainer>


            <ControlPadContainer>

                
            <SpeedSliderContainer>
            <SliderText>속도: {value}</SliderText>
            <StyledSlider
                minimumValue={0}
                maximumValue={10}
                step={1}
                value={value}
                onValueChange={handleValueChange}
                minimumTrackTintColor="#1EB1FC"
                maximumTrackTintColor="#d3d3d3"
                thumbTintColor="#1EB1FC"
                style={{ transform: [{ rotate: '-90deg' }] }} // 슬라이더 회전
            />
            </SpeedSliderContainer>

            <ButtonContainer>
                <UpButtonContainer>
                    <ButtonStyle
                        onPressIn={() => handleButtonPressIn('up')}
                        onPressOut={() => handleButtonPressOut('up')}
                    >
                        <ButtonText>{isUpPressed ? '↑' : '↑'}</ButtonText>
                    </ButtonStyle>
                </UpButtonContainer>
                <DirectionButtonContainer>
                    <ButtonStyle
                        onPressIn={() => handleButtonPressIn('left')}
                        onPressOut={() => handleButtonPressOut('left')}
                    >
                        <ButtonText>{isLeftPressed ? '←' : '←'}</ButtonText>
                    </ButtonStyle>
                    <ButtonStyle
                        onPressIn={() => handleButtonPressIn('right')}
                        onPressOut={() => handleButtonPressOut('right')}
                    >
                        <ButtonText>{isRightPressed ? '→' : '→'}</ButtonText>
                    </ButtonStyle>
                </DirectionButtonContainer>
                <DownButtonContainer>
                    <ButtonStyle
                        onPressIn={() => handleButtonPressIn('down')}
                        onPressOut={() => handleButtonPressOut('down')}
                    >
                        <ButtonText>{isDownPressed ? '↓' : '↓'}</ButtonText>
                    </ButtonStyle>
                </DownButtonContainer>
            </ButtonContainer>
            
            </ControlPadContainer>
            

            </Border2Container>


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
    background-color: #1B0C5D;
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
    border: 1px solid #FFFFFF;
    width: ${width * 0.90}px;
    margin: 2%;
`;

const Border2Container = styled.View`
    background-color: #2D1F80;
    border: 2px solid #F8098B;
    border-radius: 10px;
    padding: 10px;
    width: ${width * 0.95}px;
    margin-top: 10px;
`;

const ButtonContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-left: 10px;
`;

const UpButtonContainer = styled.View`
    margin-bottom: 20px;
    margin-left: 15px;
`;

const DirectionButtonContainer = styled.View`
    flex-direction: row;
    justify-content: space-between;
    margin-bottom: 20px;
    width: 300px;
`;

const DownButtonContainer = styled.View`
    margin-top: 0px;
    margin-left: 15px;
`;


const ButtonText = styled.Text`
    color: black;
    font-size: ${scale * 25}px; 
    font-weight: bold;
`;

const SpeedButtonText = styled.Text`
    color: white;
    font-size: ${scale * 25}px; 
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
    padding: 5px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: ${scale * 18}px; 
    font-weight: bold;
`;

const OnOffButton = styled.TouchableOpacity`
    width: ${scale * 100}px; 
    height: ${scale * 50}px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isOn }) => (isOn ? '#AAAAAA' : '#F8098B')};
    border-radius: 10px;
    padding: 10px 10px;
    margin-left: 15px;
`;

const OnOffButtonText = styled.Text`
    color: white;
    font-size: ${scale * 18}px;
    font-weight: bold;
`;

const ValueText = styled.Text`
    color: white;
    font-size: ${scale * 24}px; 
    margin-top: 10px;
    margin-bottom: 10px;
`;

const ButtonStyle = styled.TouchableOpacity`
    background-color: white;
    border-radius: 10px;
    padding: 10px 30px;
    margin: 0 40px;
    width: ${scale * 100}px; 
    justify-content: center;
    align-items: center;
`;

const SpeedButton = styled.TouchableOpacity`
    background-color: #F8098B;
    border-radius: 10px;
    padding: 10px 20px;
    margin: 10px;
    width: ${scale * 100}px; 
    justify-content: center;
    align-items: center;
`;

const CaptureButtonStyle = styled.TouchableOpacity`
    width: ${scale * 120}px; 
    height: ${scale * 50}px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isCaptureVideoPressed }) => (isCaptureVideoPressed ? '#AAAAAA' : 'white')};
    border-radius: 10px;
    padding: 10px 10px;
    margin: 0 10px;
`;

const ImageContainer = styled.View`
    width: 90%;
    height: 34%;
    border-width: 2px; 
    border-color: #F8098B;
    background-color: #222222; 
`;

const StyledImage = styled.Image`
    width: 100%;
    height: 100%;
`;

const SliderText = styled(Text)`
    font-size: 20px;
    margin-bottom: 70px;
    color: white;
`;

const StyledSlider = styled(Slider)`
    height: 10px;
    width: 150px;
    transform: rotate(-90deg);
`;


const StyledWebView = styled(WebView)`
  flex: 1;
`;




// const ImageContainer = styled.View`
//     width: 90%;  // 이미지보다 작은 너비
//     height: 50%; // 이미지보다 작은 높이
//     border-width: 2px; // 테두리 두께
//     border-color: white; // 테두리 색상
//     background-color: #222222; // 배경 색상
//     justify-content: center; // 내용 중앙 정렬
//     align-items: center; // 내용 중앙 정렬
//     border-radius: 10px; // 모서리 둥글게
// `;

// const StyledImage = styled.Image`
//     width: 90%;  // 줄어든 이미지 크기
//     height: 100%; // 줄어든 이미지 높이
// `;