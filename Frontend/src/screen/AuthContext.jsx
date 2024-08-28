import React, { createContext, useState } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const login = () => {
    setIsLoggedIn(true);
  };

  const logout = async () => {
    try {
      // AsyncStorage에서 사용자 정보 제거
      await AsyncStorage.removeItem('userInfo');
      setIsLoggedIn(false);

    } catch (error) {
      // AsyncStorage에 데이터가 없어도 에러가 발생하지 않도록 처리
      if (error.name === 'error') {
        console.log('사용자 정보가 이미 제거되어 있습니다.');
      } else {
        //console.error('로그아웃 실패', error);
      }
      setIsLoggedIn(false);
    }
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};