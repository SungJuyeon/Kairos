import React, { useState, useEffect } from 'react';
import { FlatList, Text, View, ScrollView, Alert } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { Calendar } from 'react-native-calendars';
import DateTimePicker from '@react-native-community/datetimepicker';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function ScheduleManage() {
    const { navigate } = useNavigation();

    const [selectedDate, setSelectedDate] = useState(new Date());
    const [showPicker, setShowPicker] = useState(false);
    const [task, setTask] = useState('');
    const [schedules, setSchedules] = useState([]);
    const [userName, setUserName] = useState(''); // 사용자 이름 상태 추가

    // 사용자 이름 가져오기
    const fetchUserName = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch('http://localhost:8080/user/nickname', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('사용자 이름을 가져오는 데 실패했습니다.');
            }

            const nickname = await response.text(); // 문자열로 받기
            setUserName(nickname);
        } catch (error) {
            Alert.alert('오류 발생', error.message);
            console.error('Fetch User Name Error:', error);
        }
    };

    // 서버에서 일정 가져오기
    const fetchSchedules = async () => {
        try {
            const accessToken = await AsyncStorage.getItem('token');
            const response = await fetch('http://localhost:8000/calendar', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('일정을 가져오는 데 실패했습니다.');
            }

            const data = await response.json();
            const formattedSchedules = Object.entries(data.schedules).flatMap(([date, tasks]) =>
                tasks.map(task => ({
                    id: task.id, // 서버에서 제공하는 id 사용
                    date: new Date(`${date}T${task.time}`),
                    task: task.task,
                    user_name: task.user_name
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
            const response = await fetch('http://localhost:8000/schedules/add', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_name: userName, // 사용자 이름을 실제 사용자로 대체
                    task: task,
                    date: selectedDate.toISOString().split('T')[0], // 날짜 형식
                    time: selectedDate.toTimeString().split(' ')[0].substring(0, 5), // 시간 형식
                }),
            });

            if (!response.ok) {
                throw new Error('일정을 추가하는 데 실패했습니다.');
            }

            const newSchedule = {
                id: Math.random().toString(),
                date: selectedDate.toISOString(),
                task,
                user_name: userName, // 사용자 이름을 실제 사용자로 대체
            };
            setSchedules([...schedules, newSchedule]);
            setSelectedDate(new Date());
            setTask('');
            setShowPicker(false); // 일정 추가 후 picker 닫기
        } catch (error) {
            Alert.alert('오류 발생', error.message);
        }
    };


    const removeSchedule = async (id) => {
        const scheduleToRemove = schedules.find(schedule => schedule.id === id);
    
        if (!scheduleToRemove) {
            console.log(`일정을 찾을 수 없습니다: id=${id}`);
            return; // 일정을 찾지 못하면 함수 종료
        }
    
        console.log(`삭제할 일정: ${JSON.stringify(scheduleToRemove)}`);
    
        try {
            
            // ID를 정수로 변환
            const scheduleId = parseInt(scheduleToRemove.id, 10); // 10진수로 변환


            console.log(scheduleId);
            console.log(scheduleId);
            console.log(scheduleId);
            console.log(scheduleId);
    
            const response = await fetch(`http://localhost:8000/schedules/${scheduleId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
    
            console.log(`삭제 요청 응답 상태: ${response.status}`);
    
            if (!response.ok) {
                const errorText = await response.text(); // 오류 메시지 가져오기
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
            setShowPicker(false); // 사용자가 취소할 경우
        }
    };

    useEffect(() => {
        fetchUserName(); // 컴포넌트가 마운트될 때 사용자 이름 가져오기
        fetchSchedules(); // 컴포넌트가 마운트될 때 일정 가져오기
    }, []);

    return (
        <Container>
            <ScrollView contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', alignItems: 'center' }}>
                <Title>일정 관리</Title>
                <Calendar
                    onDayPress={(day) => {
                        setSelectedDate(new Date(day.dateString));
                        setShowPicker(true); // 날짜 선택 시 picker 열기
                    }}
                    markedDates={{
                        [selectedDate.toISOString().split('T')[0]]: { selected: true, marked: true, selectedColor: 'black' },
                    }}
                    style={{ marginBottom: 20 }}
                />
                <Input
                    placeholder="할 일"
                    placeholderTextColor={'#FFFFFF'}
                    value={task}
                    onChangeText={setTask}
                />
                <Button onPress={addSchedule} activeOpacity={0.7}>
                    <ButtonText>일정 추가</ButtonText>
                </Button>

                {showPicker && (
                    <DateTimePicker
                        value={selectedDate}
                        mode="datetime"
                        display="default"
                        onChange={onChange}
                    />
                )}

                <FlatList
                    data={schedules.sort((a, b) => new Date(a.date) - new Date(b.date))}
                    keyExtractor={item => item.id}
                    renderItem={({ item }) => (
                        <ScheduleItem>
                            <ScheduleText>{`${new Date(item.date).toLocaleString()}: ${item.task} (by ${item.user_name})`}</ScheduleText>
                            <Button2 onPress={() => removeSchedule(item.id)} activeOpacity={0.7}>
                                <ButtonText>제거</ButtonText>
                            </Button2>
                        </ScheduleItem>
                    )}
                />
            </ScrollView>
        </Container>
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

const Input = styled.TextInput`
  border: 1px solid #ccc;
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
  margin: 5px;
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
