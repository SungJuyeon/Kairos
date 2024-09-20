import React, { useState } from 'react';
import { FlatList, Text, View, ScrollView } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";
import { Calendar } from 'react-native-calendars';
import DateTimePicker from '@react-native-community/datetimepicker';

export default function ScheduleManage() {
    const { navigate } = useNavigation();

    const [selectedDate, setSelectedDate] = useState(new Date());
    const [showPicker, setShowPicker] = useState(false);
    const [task, setTask] = useState('');
    const [schedules, setSchedules] = useState([]);

    const addSchedule = () => {
        if (task) {
            setSchedules([...schedules, { id: Math.random().toString(), date: selectedDate.toISOString(), task }]);
            setSelectedDate(new Date());
            setTask('');
            setShowPicker(false); // 일정 추가 후 picker 닫기
        }
    };

    const removeSchedule = (id) => {
        setSchedules(schedules.filter(schedule => schedule.id !== id));
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
                        <ScheduleText>{`${new Date(item.date).toLocaleString()}: ${item.task}`}</ScheduleText>
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
