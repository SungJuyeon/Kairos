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
                style={{ width: 640, height: 230 }}
            />
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
            </CaptureButtonContainer>
            <RemoveContainer>
            <StyledText>인물 제거 모드 : </StyledText>
            <OnOffButton
                onPress={handleOnOffPress}
                isOn={isOn}>
                <OnOffButtonText isOn={isOn}>{isOn ? '적용 중' : '적용'}</OnOffButtonText>
            </OnOffButton>
            </RemoveContainer>
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
    margin-top: 25px;
`;

const Container = styled.SafeAreaView`
    background-color: #000000;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const ButtonContainer = styled.View`
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
    margin-bottom: 20px;
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

const CaptureButtonStyle = styled.TouchableOpacity`
    background-color: ${({isCaptureVideoPressed}) => (isCaptureVideoPressed ? '#AAAAAA' : 'white')};
    border-radius: 10px;
    padding: 20px 20px;
    margin: 0 10px;
`;

const CaptureButtonText = styled.Text`
    color: black;
    font-size: 18px;
    font-weight: bold;
`;

const OnOffButton = styled.TouchableOpacity`
    background-color: ${({ isOn }) => (isOn ? 'gray' : 'white')};
    border-radius: 10px;
    padding: 10px 20px;
`;

const OnOffButtonText = styled.Text`
    color: ${({ isOn }) => (isOn ? 'white' : 'black')};
    font-size: 18px;
    font-weight: bold;
`;