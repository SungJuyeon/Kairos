import React, { useState, useEffect } from "react";
import { SafeAreaView } from "react-native";
import { useNavigation } from "@react-navigation/native";
import styled from 'styled-components/native';
import axios from 'axios';

export default function Density() {
    const { navigate } = useNavigation();

    // 각 장소의 밀집도 저장
    const [densities, setDensities] = useState({
        ssPark: 30,
        ssBase: 30,
        ssCommons: 30,
        creativeRoom: 50,
        focusRoom: 80,
        restaurant: 10
    });

    // 서버로부터 밀집도 데이터를 요청 후 저장
    const fetchDensityData = async () => {
        try {
            const response = await axios.get('[REST API를 만족하는 주소]');
            // 임시로 주석 처리
            // setDensities(response.data); // 서버에서 받은 데이터로 상태 업데이트
        } catch (error) {
            console.error("데이터 요청 실패:", error);
        }
    };

    // 컴포넌트가 마운트 될 때 혹은 1분마다 데이터 요청
    useEffect(() => {
        fetchDensityData(); // 컴포넌트가 마운트될 때 데이터 요청

        const interval = setInterval(() => {
            fetchDensityData(); // 1분마다 데이터 요청
        }, 60000);

        return () => clearInterval(interval); // 컴포넌트 언마운트 시 인터벌 클리어
    }, []);

    // 밀집도에 따라 여유, 보통, 혼잡으로 출력
    const getDensityStatus = (density) => {
        if (density < 30) return '여유';
        else if (density < 70) return '보통';
        else return '혼잡';
    };

    return (
        <Container>
            <Title>밀집도 현황</Title>
            <DensityContainer>
                <DensityItem>
                    <Location>상상 파크:</Location>
                    <Status>{getDensityStatus(densities.ssPark)}</Status>
                </DensityItem>
                <DensityItem>
                    <Location>상상 베이스:</Location>
                    <Status>{getDensityStatus(densities.ssBase)}</Status>
                </DensityItem>
                <DensityItem>
                    <Location>상상 커먼스:</Location>
                    <Status>{getDensityStatus(densities.ssCommons)}</Status>
                </DensityItem>
                <DensityItem>
                    <Location>창의 열람실:</Location>
                    <Status>{getDensityStatus(densities.creativeRoom)}</Status>
                </DensityItem>
                <DensityItem>
                    <Location>집중 열람실:</Location>
                    <Status>{getDensityStatus(densities.focusRoom)}</Status>
                </DensityItem>
                <DensityItem>
                    <Location>학식당:</Location>
                    <Status>{getDensityStatus(densities.restaurant)}</Status>
                </DensityItem>
            </DensityContainer>
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 50px;
    margin-bottom: 20px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #000000;
    flex: 1;
    justify-content: center;
    align-items: center;
`;

const DensityContainer = styled.View`
    align-items: flex-start;
`;

const DensityItem = styled.View`
    flex-direction: row;
    align-items: center;
    margin-bottom: 20px;
`;

const Location = styled.Text`
    color: white;
    font-size: 30px;
    margin-right: 10px;
`;

const Status = styled.Text`
    color: white;
    font-size: 30px;
`;