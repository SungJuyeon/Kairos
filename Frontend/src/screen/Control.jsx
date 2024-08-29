import React, { useState, useEffect } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, Alert, PermissionsAndroid, Platform, Dimensions } from "react-native";
import styled from 'styled-components/native';
import * as FileSystem from 'expo-file-system';
import * as ImagePicker from 'expo-image-picker';

import Slider from '@react-native-community/slider';


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


    const [speed, setSpeed] = useState(5); // 기본 속도
    const [prevSpeed, setPrevSpeed] = useState(5); // 이전 속도 저장



    const imageURL = `${BASE_URL}/video_feed`;

    // 속도 조절
    const [value, setValue] = useState(5);

    const increment = () => {
      setValue(prevValue => Math.min(prevValue + 1, 10)); // 최대값 10으로 제한
    };
  
    const decrement = () => {
      setValue(prevValue => Math.max(prevValue - 1, 1)); // 최소값 1으로 제한
    };

    
    //const BASE_URL = 'http://172.30.1.68:8000'; //
    const BASE_URL = 'http://223.194.130.159:8000'; // 학교
    //const BASE_URL = 'http://localhost:8000'; // 라즈베리파이 서버 URL


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


async function handleCapturePhoto(imageUrl) {
    try {
        if (Platform.OS === 'web') {
            // 웹 플랫폼에서 이미지를 다운로드
            await downloadImage();

        } else {
            // 네이티브 플랫폼에서 expo-file-system 사용
            const response = await fetch(imageUrl);
            if (!response.ok) {
                throw new Error('Failed to fetch image from URL');
            }
            const imageData = await response.blob(); // Blob으로 변환
            const base64Data = await convertBlobToBase64(imageData); // Base64로 변환
            await FileSystem.writeAsStringAsync(FileSystem.documentDirectory + 'image.jpg', base64Data, {
                encoding: FileSystem.EncodingType.Base64,
            });
            console.log('Image saved to file system');
        }
    } catch (error) {
        console.error('Error saving image:', error);
    }
}



async function downloadImage() {
    try {
        console.log('Fetching image from URL:', 'http://localhost:8000/video_feed');

        const response = await fetch('http://localhost:8000/video_feed');
        console.log('Response status:', response.status);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let accumulatedChunk = ''; // 청크를 누적할 변수 추가
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) {
                console.log('Stream reading finished.');
                break;
            }

            // Read chunk and decode
            accumulatedChunk += decoder.decode(value, { stream: true });
            console.log('Current accumulated chunk length:', accumulatedChunk.length);

            // 'frame' 경계로 이미지 파싱
            let startIndex = accumulatedChunk.indexOf('--frame');
            while (startIndex !== -1) {
                console.log('Frame start found at index:', startIndex);

                // 다음 프레임 시작 위치로 이동
                let headerEndIndex = accumulatedChunk.indexOf('\r\n\r\n', startIndex) + 4;
                const endIndex = accumulatedChunk.indexOf('\r\n--frame', headerEndIndex);
                
                if (endIndex !== -1) {
                    console.log('Frame end found at index:', endIndex);

                    // JPEG 이미지 데이터 추출
                    const imageData = accumulatedChunk.slice(headerEndIndex, endIndex);
                    console.log('Extracted image data length:', imageData.length);

                    const byteArray = new Uint8Array(imageData.length);
                    for (let i = 0; i < imageData.length; i++) {
                        byteArray[i] = imageData.charCodeAt(i);
                    }

                    console.log('Byte array created with length:', byteArray.length);
                    
                    // Blob 생성
                    const blob = new Blob([byteArray], { type: 'image/jpeg' });
                    console.log('Blob created successfully.');

                    // 이미지 저장 로직
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'image.jpg'; // 저장할 파일 이름
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                    URL.revokeObjectURL(url);
                    console.log('Image downloaded successfully');
                    break; // 첫 번째 이미지만 처리
                } else {
                    console.log('End of frame not found in accumulated chunk.');
                    break; // 다음 루프에서 계속 시도
                }
            }

            // 마지막 청크가 남아있을 경우, 계속해서 누적
            if (startIndex === -1) {
                console.log('Frame start not found in current accumulated chunk.');
                // 누적된 청크가 너무 커지면 자르기
                if (accumulatedChunk.length > 100000) {
                    accumulatedChunk = accumulatedChunk.slice(accumulatedChunk.indexOf('--frame'));
                }
            }
        }
    } catch (error) {
        console.error('Error downloading image:', error);
    }
}

const openGallery = async () => {
    // 권한 요청
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permission.granted) {
        // 갤러리 열기
        const result = await ImagePicker.launchImageLibraryAsync();
        if (!result.cancelled) {

        }
    } else {
        Alert.alert('권한이 필요합니다!', '갤러리에 접근할 수 있는 권한이 필요합니다.');
    }
};

async function convertBlobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result.split(',')[1]); // Base64 데이터만 반환
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

    

    // 동영상 촬영 버튼 클릭 시
    const handleCaptureVideo = () => {
        setIsCaptureVideoPressed(!isCaptureVideoPressed);
        // 동영상 촬영 기능 구현
    };

    // on/off 버튼 클릭 시
    const handleOnOffPress = () => {
        setIsOn(!isOn);
    };


    useEffect(() => {
        const updateSpeed = async () => {
          if (speed > prevSpeed) {
            await fetch(`${BASE_URL}/speed/up`, { method: 'POST' });
          } else if (speed < prevSpeed) {
            await fetch(`${BASE_URL}/speed/down`, { method: 'POST' });
          }
          setPrevSpeed(speed); // 현재 속도를 이전 속도로 업데이트
        };
    
        updateSpeed();
      }, [speed]);





    return (
        <Container>

            <MarginContainer />

            <ImageContainer>
                <StyledImage
                    source={{ uri: `${BASE_URL}/video_feed` }}
                />
            </ImageContainer>

            <Margin2Container />
            <BorderContainer></BorderContainer>

            <Border2Container>

            <CaptureButtonContainer>
                <CaptureButtonStyle
                    onPress={handleCapturePhoto}
                >
                    <CaptureButtonText>Picture</CaptureButtonText>
                </CaptureButtonStyle>
                <CaptureButtonStyle
                    isCaptureVideoPressed={isCaptureVideoPressed}
                    onPress={handleCaptureVideo}
                >
                    <CaptureButtonText>{isCaptureVideoPressed ? 'Recoding' : 'Recode'}</CaptureButtonText>
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

            {/* <SpeedButtonContainer>
                <ValueText>Speed: {value}</ValueText>
                <SpeedButton onPress={increment}>
                <SpeedButtonText>UP</SpeedButtonText>
                </SpeedButton>
                <SpeedButton onPress={decrement}>
                <SpeedButtonText>DOWN</SpeedButtonText>
                </SpeedButton>    
            </SpeedButtonContainer> */}

            <SliderContainer>
                <SliderText>{speed}</SliderText>
                <StyledSlider
                    minimumValue={0}
                    maximumValue={10}
                    step={1}
                    value={speed}
                    onValueChange={setSpeed}
                    minimumTrackTintColor="#1fb28a"
                    maximumTrackTintColor="#d3d3d3"
                    thumbTintColor="#f5fcff"
                />
            </SliderContainer>


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
    margin-right: 70px;
`;

const UpButtonContainer = styled.View`
    margin-bottom: 20px;
    margin-left: 70px;
`;

const DirectionButtonContainer = styled.View`
    flex-direction: row;
    justify-content: space-between;
    margin-bottom: 20px;
    width: 200px;
`;

const DownButtonContainer = styled.View`
    margin-top: 0px;
    margin-left: 70px;
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

const SpeedButtonContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border: 2px solid #F8098B;
    border-radius: 10px;
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
    height: 45%;
    border-width: 2px; 
    border-color: #F8098B;
    background-color: #222222; 
    justify-content: center;
    align-items: center;
`;

const StyledImage = styled.Image`
    width: 100%;
    height: 100%;
`;

const SliderContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 5px;
    margin-left: 0px;
`;

const SliderText = styled.Text`
    font-size: 20px;
    margin-bottom: 50px;
    color: #FFFFFF;
`;

const StyledSlider = styled(Slider)`
    width: 120px; /* 너비를 좁게 설정 */
    height: 100px; /* 높이 설정 */
    transform: rotate(-90deg); /* 슬라이더를 90도 회전 */
    margin-bottom: 20px;
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