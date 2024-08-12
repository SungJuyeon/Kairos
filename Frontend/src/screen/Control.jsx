import React, { useState } from "react";
import { SafeAreaView, Image, View, TouchableOpacity, Alert, PermissionsAndroid } from "react-native";
import CameraRoll from '@react-native-community/cameraroll';
import styled from 'styled-components/native';



export default function Control() {
    const [isUpPressed, setIsUpPressed] = useState(false);
    const [isLeftPressed, setIsLeftPressed] = useState(false);
    const [isRightPressed, setIsRightPressed] = useState(false);
    const [isDownPressed, setIsDownPressed] = useState(false);
    const [isCaptureVideoPressed, setIsCaptureVideoPressed] = useState(false);
    const [isOn, setIsOn] = useState(false); // on/off 상태 추가

    // 속도 조절
    const [value, setValue] = useState(1);

    const increment = () => {
      setValue(prevValue => Math.min(prevValue + 1, 10)); // 최대값 10으로 제한
    };
  
    const decrement = () => {
      setValue(prevValue => Math.max(prevValue - 1, 1)); // 최소값 1으로 제한
    };

    
    //const BASE_URL = 'http://172.30.1.36:8000'; // 라즈베리파이 서버 URL
    //const BASE_URL = 'http://172.20.10.4:8000'; // 라즈베리파이 서버 URL
    const BASE_URL = 'http://223.194.136.129:8000'; // 라즈베리파이 서버 URL


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


    // 사진 촬영 버튼 클릭 시
    const handleCapturePhoto = async () => {

        // 안드로이드에서 사진 저장 권한을 받기 위함
        // const hasPermission = await requestCameraRollPermission();
        // if (!hasPermission) {
        //     Alert.alert('권한 없음', '사진을 저장하기 위한 권한이 필요합니다.');
        //     return;
        // }

        

        try {

            // const { status } = await MediaLibrary.requestPermissionsAsync();
            // status === 'granted';
            const result = await CameraRoll.save(imageUrl, { type: 'photo' });
            Alert.alert('사진 저장 완료', '사진이 갤러리에 저장되었습니다.');
            console.log(result); // result를 출력
        } catch (error) {
            Alert.alert('저장 실패', '사진 저장 중 오류가 발생했습니다.');
            console.log(error); // 에러를 출력
        }
    };


    // 동영상 촬영 버튼 클릭 시
    const handleCaptureVideo = () => {
        setIsCaptureVideoPressed(!isCaptureVideoPressed);
        // 동영상 촬영 기능 구현
    };

    // on/off 버튼 클릭 시
    const handleOnOffPress = () => {
        setIsOn(!isOn);
    };

    return (
        <Container>
           <Image
                source={{ uri: `${BASE_URL}/video_feed` }}
                style={{ width: 640, height: 360 }}
            />

            <BorderContainer>
            <ControlPadContainer>
            <SpeedButtonContainer>
                <ValueText>속도: {value}</ValueText>
                <SpeedButton onPress={increment}>
                <ButtonText>증가</ButtonText>
                </SpeedButton>
                <SpeedButton onPress={decrement}>
                <ButtonText>감소</ButtonText>
                </SpeedButton>
            </SpeedButtonContainer>

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
            
            <CaptureButtonContainer>
                <CaptureButtonStyle
                    onPress={handleCapturePhoto}
                >
                    <CaptureButtonText>사진 촬영</CaptureButtonText>
                </CaptureButtonStyle>
                <CaptureButtonStyle
                    isCaptureVideoPressed={isCaptureVideoPressed}
                    onPress={handleCaptureVideo}
                >
                    <CaptureButtonText>{isCaptureVideoPressed ? '동영상 촬영 중...' : '동영상 촬영'}</CaptureButtonText>
                </CaptureButtonStyle>
                <RemoveContainer>
                    <StyledText>인물 제거 모드 : </StyledText>
                    <OnOffButton
                        onPress={handleOnOffPress}
                        isOn={isOn}>
                        <OnOffButtonText isOn={isOn}>{isOn ? '적용 중...' : '적용'}</OnOffButtonText>
                    </OnOffButton>
                </RemoveContainer>
            </CaptureButtonContainer>
            </BorderContainer>


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

const BorderContainer = styled.View`
    border: 2px solid #FFF;
    border-radius: 10px;
    padding: 20px;
;`

const ButtonContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-left: 30px;
`;

const UpButtonContainer = styled.View`
    margin-bottom: 20px;
`;

const DirectionButtonContainer = styled.View`
    flex-direction: row;
    justify-content: space-between;
    margin-bottom: 20px;
    width: 300px;
`;

const DownButtonContainer = styled.View`
    margin-top: 0px;
`;

const ButtonStyle = styled.TouchableOpacity`
  background-color: white;
  border-radius: 10px;
  padding: 10px 20px;
  margin: 0 40px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 25px;
    font-weight: bold;
`;

const CaptureButtonContainer = styled.View`
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
`;

const ControlPadContainer = styled.View`
    flex-direction: row;
    justify-content: center;
    align-items: center;
`;

const SpeedButtonContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border: 2px solid #FFF;
    border-radius: 10px;
    padding: 20px;
`;

// border: 2px solid #000; // 테두리 두께와 색상
// border-radius: 10px; // 모서리 둥글기 (선택 사항)
// padding: 20px; // 내부 여백 (선택 사항)

const CaptureButtonStyle = styled.TouchableOpacity`
    width: 120px;
    height: 50px;
    justify-content: center;
    align-items: center;
    background-color: ${({isCaptureVideoPressed}) => (isCaptureVideoPressed ? '#AAAAAA' : 'white')};
    border-radius: 10px;
    padding: 10px 10px;
    margin: 0 10px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 18px;
    font-weight: bold;
`;

const OnOffButton = styled.TouchableOpacity`
    width: 80px;
    height: 50px;
    justify-content: center;
    align-items: center;
    background-color: ${({ isOn }) => (isOn ? '#AAAAAA' : 'white')};
    border-radius: 10px;
    padding: 10px 10px;
    margin-left: 10px;
`;

const OnOffButtonText = styled.Text`
    color: 'black';
    font-size: 18px;
    font-weight: bold;
`;

const ValueText = styled.Text`
    color: white;
    font-size: 24px;
    margin-bottom: 20px;
`;

const SpeedButton = styled.TouchableOpacity`
  background-color: white;
  border-radius: 10px;
  padding: 10px 20px;
  margin: 10px;
`;
