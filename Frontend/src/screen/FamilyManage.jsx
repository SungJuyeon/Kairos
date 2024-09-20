import React, { useState } from "react";
import { FlatList, Image } from "react-native";
import styled from 'styled-components/native';
import { useNavigation } from "@react-navigation/native";

const initialData = [
    { id: '1', title: '엄마', image: require('./../../assets/mom.jpg') },
    { id: '2', title: '아빠', image: require('./../../assets/dad.jpg') },
    { id: '3', title: '동생', image: require('./../../assets/duck.png') },
];

export default function FamilyManage() {
    const { navigate } = useNavigation();
    const [data, setData] = useState(initialData);

    const removeItem = (id) => {
        setData(prevData => prevData.filter(item => item.id !== id));
    };

    const renderItem = ({ item }) => (
        <Item>
            <ItemImage source={item.image} />
            <ItemText>{item.title}</ItemText>
            <RemoveButton onPress={() => removeItem(item.id)}>
                <RemoveButtonText>제거</RemoveButtonText>
            </RemoveButton>
        </Item>
    );

    return (
        <Container>
            <Title>가족 관리</Title>
            <FlatList
                data={data}
                renderItem={renderItem}
                keyExtractor={item => item.id}
                contentContainerStyle={{ paddingBottom: 20 }}
            />
            <Button onPress={() => navigate('FamilyAdd')}>
                <ButtonText>추가하기</ButtonText>
            </Button>
        </Container>
    );
}

const Title = styled.Text`
    color: white;
    font-size: 30px;
    margin-bottom: 10px;
    font-weight: bold;
`;

const Container = styled.SafeAreaView`
    background-color: #222222;
    flex: 1;
    justify-content: center;
    align-items: center;
    padding: 10px;
`;

const Item = styled.View`
    background-color: #FFFFFF;
    padding: 15px;
    border-radius: 5px;
    margin: 5px;
    width: 200px;
    align-items: center;
    height: 170px;
    justify-content: center;
`;

const ItemImage = styled.Image`
    width: 80px;
    height: 80px;
    border-radius: 40px;
    margin-bottom: 5px;
    margin-top: 5px;
`;

const ItemText = styled.Text`
    color: black;
    font-size: 16px;
    font-weight: bold;
`;

const RemoveButton = styled.TouchableOpacity`
    background-color: #FF4D4D;
    padding: 5px 10px;
    border-radius: 5px;
    margin-top: 10px;
`;

const RemoveButtonText = styled.Text`
    color: white;
    font-weight: bold;
`;

const Button = styled.TouchableOpacity`
    background-color: #FFCEFF;
    padding: 10px 20px;
    border-radius: 5px;
    margin: 5px;
`;

const ButtonText = styled.Text`
    color: black;
    font-size: 18px;
    font-weight: bold;
`;
