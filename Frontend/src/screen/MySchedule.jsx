import React, { useState } from "react";
import { View, Text, SafeAreaView, TouchableOpacity } from "react-native";
import { useNavigation } from "@react-navigation/native";
import styled from 'styled-components/native';

export default function MySchedule() {
    const { navigate } = useNavigation();

    // 캘린더에 필요한 변수들
    const daysOfWeek = ["월", "화", "수", "목", "금"];
    const rows = 10; // 행의 수
    const columns = daysOfWeek.length; // 열의 수 (요일 수)

    // 추천하는 빈 강의실
    const [lecterRoom, setLectureRoom] = useState("공학관 202호");

    // 각 셀의 내용 초기화
    const [calendarData, setCalendarData] = useState(
        Array.from({ length: rows }, () =>
            Array(columns).fill({ text: "", color: "transparent" })
        )
    );

    // 셀을 클릭할 때 셀의 값을 수정
    const handleCellPress = (rowIndex, colIndex) => {
        const newData = [...calendarData]; // 현재 상태 복사
        newData[rowIndex][colIndex] = {
            text: "클릭됨", // 원하는 값으로 업데이트
            color: "skyblue" // 원하는 색으로 변경
        };
        setCalendarData(newData); // 상태 업데이트
    };

    return (
        <Container>
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
                            <Cell key={colIndex} onPress={() => handleCellPress(rowIndex, colIndex)}>
                                <CellText>{calendarData[rowIndex][colIndex]}</CellText>
                            </Cell>
                        ))}
                    </Row>
                ))}
            </Calendar>
            <StyledText>현재 추천드리는 빈 강의실은</StyledText>
            <StyledText>{lecterRoom} 입니다!</StyledText>
        </Container>
    );
}

const Container = styled.SafeAreaView`
    background-color: #000000;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFFFFF;
    padding: 10px 20px;
    border-radius: 5px;
    margin: 5px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 16px;
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
    padding: 10px;
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
    width: 70px;
    height: 40px;
    align-items: center;
    justify-content: center;
    border: 1px solid #444444;
`;

const StyledText = styled.Text`
    color: white;
    font-size: 30px;
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

