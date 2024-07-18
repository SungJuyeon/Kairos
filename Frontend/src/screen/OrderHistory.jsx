import React from "react";
import { View, Text, SafeAreaView, Button } from "react-native";
import { useNavigation } from "@react-navigation/native";
import styled from 'styled-components/native'

export default function OrderHistory() {
    const { navigate } = useNavigation();

    return (
        <Container>
            <Button title="가게로 이동" onPress={() => navigate("Store")} />
        </Container>
    );
}

const Container = styled.SafeAreaView`
    flex: 1;
    justify-content: center;
    align-items: center;
`;