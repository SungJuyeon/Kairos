import React, { useState } from "react";
import { View, Text, SafeAreaView, TouchableOpacity, Dimensions, ScrollView } from "react-native";
import { useNavigation } from "@react-navigation/native";
import styled from 'styled-components/native';

const { width, height } = Dimensions.get('window');

export default function MySchedule() {
    const { navigate } = useNavigation();

    const daysOfWeek = ["/", "월", "화", "수", "목", "금"];
    const rows = 10;
    const columns = daysOfWeek.length;

    const [lecterRoom, setLectureRoom] = useState("공학관 202호");
    const [calendarData, setCalendarData] = useState(
        Array.from({ length: rows }, () =>
            Array.from({ length: columns }, () => ({ text: "", color: "black" })) // 각 셀에 대해 새로운 객체 생성
        )
    );

    const handleCellPress = (rowIndex, colIndex) => {
        const newData = [...calendarData];
        newData[rowIndex][colIndex] = {
            text: "클릭됨",
            color: "#0CDAE0"
        };
        setCalendarData(newData);
    };

    return (
        <Container>
            <ScrollView>
            <Button onPress={() => navigate("InputMySchedule")}>
                <ButtonText>나의 시간표 추가하기</ButtonText>
            </Button>
            <Calendar>
                <Header>
                    {daysOfWeek.map((day, index) => (
                        <HeaderCell key={index}>
                            <HeaderText>{day}</HeaderText>
                        </HeaderCell>
                    ))}
                </Header>
                {Array.from({ length: rows }).map((_, rowIndex) => (
                    <Row key={rowIndex}>
                        {Array.from({ length: columns }).map((_, colIndex) => (
                            <Cell
                                key={colIndex}
                                onPress={() => handleCellPress(rowIndex, colIndex)}
                                style={{ backgroundColor: calendarData[rowIndex][colIndex].color }}
                            >
                                <CellText>{calendarData[rowIndex][colIndex].text}</CellText>
                            </Cell>
                        ))}
                    </Row>
                ))}
            </Calendar>
            <StyledText>현재 추천드리는 빈 강의실은</StyledText>
            <StyledText>{lecterRoom} 입니다!</StyledText>
            </ScrollView>
        </Container>
    );
}

const Container = styled.SafeAreaView`
    background-color: #000000;
    justify-content: center;
    align-items: center;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: ${height * 0.02}px ${width * 0.05}px;
    border-radius: 5px;
    margin: 5px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: ${height * 0.025}px;
    font-weight: bold;
`;

const Calendar = styled.View`
    margin-top: 20px;
    border: 1px solid white;
    border-radius: 10px;
    overflow: hidden;
`;

const Header = styled.View`
    flex-direction: row;
    background-color: #444444;
`;

const HeaderCell = styled.View`
    flex: 1;
    padding: ${height * 0.02}px;
    align-items: center;
    justify-content: center;
    border-bottom-width: 1px;
    border-bottom-color: white;
`;

const Row = styled.View`
    flex-direction: row;
`;

const Cell = styled.TouchableOpacity`
    flex: 1;
    height: ${height * 0.05}px;
    align-items: center;
    justify-content: center;
    border: 1px solid #444444;
`;

const StyledText = styled.Text`
    color: white;
    font-size: ${height * 0.03}px;
    margin-top: 20px;
    margin-bottom: 5px;
    margin-left: 10px;
    font-weight: bold;
`;

const HeaderText = styled.Text`
    color: white;
    font-weight: bold;
`;

const CellText = styled.Text`
    color: white;
`;

