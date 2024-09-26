import React, { useState } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Alert, Image, ScrollView, KeyboardAvoidingView, Platform } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import * as ImagePicker from 'expo-image-picker';

const BASE_URL = 'http://172.30.1.68:8080';

export default function SignUp() {
    const { navigate } = useNavigation();

    const [password, setPassword] = useState('');
    const [confirmPW, setConfirmPW] = useState('');
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [nickname, setNickname] = useState('');
    const [selectedImage, setSelectedImage] = useState(null);

    const createMember = async () => {
        if (password !== confirmPW) {
            Alert.alert('비밀번호가 일치하지 않습니다.');
            return;
        }
    
        try {
            const formData = new FormData();
            const data = JSON.stringify({ username, password, email, nickname });
            formData.append('data', data);
    
            if (selectedImage) {
                const fileName = `${username}.jpg`; // 파일 이름을 username으로 설정
                const fileType = 'image/jpg'; // MIME 타입을 image/jpg으로 설정
    
                // FormData에 직접 이미지 URI 추가
                formData.append('file', {
                    uri: selectedImage,
                    name: fileName,
                    type: fileType,
                });
            }
    
            console.log('서버에 전송할 FormData:', formData); // FormData 로그
            const response = await fetch(`${BASE_URL}/join`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
                body: formData,
            });
    
            const responseText = await response.text();
            console.log('Response Status:', response.status);
            console.log('Response Text:', responseText);
    
            if (response.ok) {
                Alert.alert('회원가입 성공', responseText);
                navigate('Login');
            } else {
                Alert.alert('회원가입 실패', responseText);
            }
    
        } catch (error) {
            console.error('Error:', error);
            Alert.alert('오류 발생', '다시 시도해 주세요.');
        }
    };
    
    const uploadFile = async () => {
        const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

        if (permissionResult.granted === false) {
            Alert.alert('사진 라이브러리에 접근할 수 없습니다.');
            return;
        }

        const result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 1,
        });

        console.log('선택 결과:', result);
        if (result.canceled) {
            console.log('사용자에 의해 취소됨');
        } else {
            const imageUri = result.assets[0].uri;
            console.log('선택한 이미지 URI:', imageUri);
            setSelectedImage(imageUri);
        }
    };

    return (
        <KeyboardAvoidingView
            style={{ flex: 1 }} // 전체 화면을 차지하도록 설정
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'} // iOS와 Android에 따라 다르게 설정
            keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0} // 필요에 따라 조정
        >
            <Container>
                <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', alignItems: 'center' }}>
                    <Title>회원가입</Title>
                    <InputContainer>
                        <Text style={{ color: 'white', fontWeight: 'bold' }}>ID</Text>
                        <StyledTextInput
                            onChangeText={text => setUsername(text)}
                            value={username}
                        />
                        <Text style={{ color: 'white', fontWeight: 'bold' }}>비밀번호</Text>
                        <StyledTextInput
                            onChangeText={text => setPassword(text)}
                            value={password}
                            secureTextEntry={true}
                        />
                        <Text style={{ color: 'white', fontWeight: 'bold' }}>비밀번호 확인</Text>
                        <StyledTextInput
                            onChangeText={text => setConfirmPW(text)}
                            value={confirmPW}
                            secureTextEntry={true}
                        />
                        <Text style={{ color: 'white', fontWeight: 'bold' }}>E-mail</Text>
                        <StyledTextInput
                            onChangeText={text => setEmail(text)}
                            value={email}
                            keyboardType="email-address"
                            autoCapitalize="none"
                            autoCorrect={false}
                        />
                        <Text style={{ color: 'white', fontWeight: 'bold' }}>닉네임</Text>
                        <StyledTextInput
                            onChangeText={text => setNickname(text)}
                            value={nickname}
                        />
                    </InputContainer>
                    {selectedImage && (
                        <ImagePreview source={{ uri: selectedImage }} />
                    )}
                    <RowContainer>
                        <Button onPress={createMember}>
                            <ButtonText>회원 가입</ButtonText>
                        </Button>
                        <Button onPress={uploadFile}>
                            <ButtonText>사진 업로드</ButtonText>
                        </Button>
                    </RowContainer>
                </ScrollView>
            </Container>
        </KeyboardAvoidingView>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 25px;
    margin-bottom: 50px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
`;

const InputContainer = styled.View`
    width: 100%;
    padding: 0 20px;
    margin-left: 25%;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: 12px 24px;
    border-radius: 10px;
    margin: 0 10px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 16px;
    font-weight: bold;
`;

const StyledTextInput = styled.TextInput`
    height: 40px;
    width: 70%;
    border-color: white;
    border-bottom-width: 2px;
    padding: 10px;
    margin-top: 5px;
    margin-bottom: 15px;
    color: white;
    font-size: 18px;
    background-color: #222222;
`;

const RowContainer = styled.View`
    flex-direction: row;
    justify-content: left;
    align-items: left;
    margin-top: 30px;
    margin-left: 20px;
`;

const ImagePreview = styled.Image`
    width: 100%;
    height: 200px;
    margin-top: 20px;
    border-radius: 10px;
`;
