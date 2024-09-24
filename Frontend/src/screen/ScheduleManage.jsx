import React, { useState, useEffect } from 'react';
import { FlatList, Text, View, ScrollView, Alert, KeyboardAvoidingView, Platform } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { Calendar } from 'react-native-calendars';
import DateTimePicker from '@react-native-community/datetimepicker';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BASE_URL_8080 = 'http://223.194.139.32:8080';
const BASE_URL_8000 = 'http://223.194.139.32:8000';

export default function ScheduleManage() {
    const { navigate } = useNavigation();

    const [selectedDate, setSelectedDate] = useState(new Date());
    const [showPicker, setShowPicker] = useState(false);
    const [task, setTask] = useState('');
    const [schedules, setSchedules] = useState([]);
    const [userName, setUserName] = useState('');
    const [taskFocused, setTaskFocused] = useState(false);

    const fetchUserName = async () => {
        // 사용자 이름 가져오기
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch(`${BASE_URL_8080}/user/nickname`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('사용자 이름을 가져오는 데 실패했습니다.');
            }

            const nickname = await response.text();
            setUserName(nickname);
        } catch (error) {
            Alert.alert('오류 발생', error.message);
            console.error('Fetch User Name Error:', error);
        }
    };

    const fetchSchedules = async () => {
        // 서버에서 일정 가져오기
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch(`${BASE_URL_8000}/calendar`, {
                method: 'GET',
                headers: {
                    token : accessToken,
                },
            });

            if (!response.ok) {
                throw new Error('일정을 가져오는 데 실패했습니다.');
            }

            const data = await response.json();
            const formattedSchedules = Object.entries(data.schedules).flatMap(([date, tasks]) =>
                tasks.map(task => ({
                    id: task.id,
                    date: new Date(`${date}T${task.time}`),
                    task: task.task,
                    user_name: task.user_name,
                    time: task.time, // 추가된 time
                }))
            );

            setSchedules(formattedSchedules);
        } catch (error) {
            Alert.alert('오류 발생', error.message);
            console.error('Fetch Schedules Error:', error);
        }
    };

    const addSchedule = async () => {
        if (!task) {
            Alert.alert('오류', '할 일을 입력해주세요.');
            return;
        }

        try {
            const accessToken = await AsyncStorage.getItem('token');

            // 새로운 ID 생성
            const newId = schedules.length > 0 ? Math.max(...schedules.map(s => s.id)) + 1 : 1;

            const response = await fetch(`${BASE_URL_8000}/schedules/add`, {
                method: 'POST',
                headers: {
                    'token': `${accessToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_name: userName,
                    task: task,
                    date: selectedDate.toISOString().split('T')[0],
                    time: selectedDate.toTimeString().split(' ')[0].substring(0, 5),
                }),
            });

            if (!response.ok) {
                throw new Error('일정을 추가하는 데 실패했습니다.');
            }

            const newSchedule = {
                id: newId, // 새로 생성한 ID
                date: selectedDate.toISOString(),
                task,
                user_name: userName,
                time: selectedDate.toTimeString().split(' ')[0].substring(0, 5), // 추가된 time
            };
            setSchedules([...schedules, newSchedule]);
            setSelectedDate(new Date());
            setTask('');
            setShowPicker(false);
        } catch (error) {
            Alert.alert('오류 발생', error.message);
        }
    };

    const removeSchedule = async (id) => {
        const scheduleToRemove = schedules.find(schedule => schedule.id === id);
    
        if (!scheduleToRemove) {
            console.log(`일정을 찾을 수 없습니다: id=${id}`);
            return;
        }
    
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch(`${BASE_URL_8000}/schedules/${id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'token' : `${accessToken}`,
                },
            });
    
            if (!response.ok) {
                const errorText = await response.text();
                console.error('삭제 요청 오류:', errorText);
                throw new Error('일정을 삭제하는 데 실패했습니다.');
            }
    
            setSchedules(schedules.filter(schedule => schedule.id !== id));
        } catch (error) {
            Alert.alert('오류 발생', error.message);
            console.error('Remove Schedule Error:', error);
        }
    };

    const onChange = (event, selectedDate) => {
        if (event.type === 'set') {
            const currentDate = selectedDate || new Date();
            setShowPicker(false);
            setSelectedDate(currentDate);
        } else {
            setShowPicker(false);
        }
    };

    useEffect(() => {
        fetchUserName();
        fetchSchedules();
    }, []);

    return (
        <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
        >
            <Container>
                <ScrollContainer>
                    <Title>일정 관리</Title>
                    <Calendar
                        onDayPress={(day) => {
                            setSelectedDate(new Date(day.dateString));
                            setShowPicker(true);
                        }}
                        markedDates={{
                            [selectedDate.toISOString().split('T')[0]]: { selected: true, marked: true, selectedColor: 'black' },
                        }}
                        theme={{
                            backgroundColor: '#222222', // 캘린더 배경색
                            calendarBackground: '#222222', // 캘린더 배경색
                            textSectionTitleColor: '#FFFFFF', // 섹션 제목 색상
                            selectedDayBackgroundColor: '#FFCEFF', // 선택된 날짜 배경색
                            selectedDayTextColor: '#fff', // 선택된 날짜 텍스트 색상
                            todayTextColor: '#FFCEFF', // 오늘 날짜 텍스트 색상
                            dayTextColor: '#FFFFFF', // 일반 날짜 텍스트 색상
                            monthTextColor: '#FFFFFF', // 월 텍스트 색상
                            arrowColor: '#FFFFFF', // 화살표 색상
                            indicatorColor: '#FFFFFF', // 마킹 색상
                        }}
                        style={{ marginBottom: 20 }}
                    />
                    {showPicker && (
                        <DateTimePickerContainer>
                            <DateTimePicker
                                value={selectedDate}
                                mode="datetime"
                                display="default"
                                onChange={onChange}
                                style={{ backgroundColor: '#EEEEEE' }} // 배경색 설정
                            />
                        </DateTimePickerContainer>
                    )}
                    <StyledTextInput
                        placeholder="할 일 내용"
                        placeholderTextColor={'#FFFFFF'}
                        value={task}
                        onFocus={() => setTaskFocused(true)}
                        onBlur={() => setTaskFocused(false)}
                        onChangeText={setTask}
                        focused={taskFocused}
                    />
                    <Button onPress={addSchedule} activeOpacity={0.7}>
                        <ButtonText>일정 추가</ButtonText>
                    </Button>

 

                    <FlatList
                        data={schedules.sort((a, b) => new Date(a.date) - new Date(b.date))}
                        keyExtractor={item => item.id.toString()} // ID를 문자열로 변환
                        renderItem={({ item }) => (
                            <ScheduleItem>
                                <ScheduleText>{`날짜: ${item.date.toLocaleString()}\n할 일: ${item.task}\n사용자: ${item.user_name}`}</ScheduleText>
                                <Button2 onPress={() => removeSchedule(item.id)} activeOpacity={0.7}>
                                    <ButtonText>제거</ButtonText>
                                </Button2>
                            </ScheduleItem>
                        )}
                    />
                </ScrollContainer>
            </Container>
        </KeyboardAvoidingView>
    );
};


const Title = styled.Text`
    color: white;
    font-size: 36px;
    margin-bottom: 40px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
  flex: 1;
  padding: 20px;
  align-items: center;
  justify-content: center;
  background-color: #222222;
`;

const ScrollContainer = styled.ScrollView`
  width: 100%; /* 스크롤 뷰의 넓이를 100%로 설정 */
  padding: 10px; /* 여백 추가 */
`;

const Input = styled.TextInput`
  border: 1px solid #ccc;
  margin-top: 10px;
  margin-bottom: 10px;
  padding: 10px;
  color: white; /* 텍스트 색상 추가 */
`;

const ScheduleItem = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin-vertical: 5px;
  background-color: #222222; /* 항목 배경색 추가 */
  padding: 10px; /* 패딩 추가 */
  border-radius: 5px; /* 모서리 둥글게 */
`;

const ScheduleText = styled.Text`
  color: white; /* 텍스트 색상 변경 */
`;

const Button = styled.TouchableOpacity`
  background-color: #FFCEFF;
  padding: 10px 20px;
  border-radius: 5px;
`;

const ButtonText = styled.Text`
  color: black;
  font-size: 16px;
  font-weight: bold;
`;

const Button2 = styled.TouchableOpacity`
  background-color: #ADCDFF;
  padding: 10px 20px;
  border-radius: 5px;
  margin: 5px;
`;

const DateTimePickerContainer = styled.View`
    background-color: #EEEEEE; /* 배경색 설정 */
    padding: 5px; /* 여백 추가 */
    border-radius: 10px; /* 모서리 둥글게 */
`;

const StyledTextInput = styled.TextInput`
    height: 50px;
    width: 100%;
    border-color: ${({ focused }) => (focused ? '#FFB0F9' : '#FFB0F9')};
    border-bottom-width: 3px;
    padding: 10px;
    margin: 10px 0;
    color: white;
    font-size: 16px;
    background-color: #222222;
`;
