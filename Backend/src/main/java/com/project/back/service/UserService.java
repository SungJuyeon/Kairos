package com.project.back.service;

import com.project.back.entity.UserEntity;
import com.project.back.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserService {

    @Autowired
    private UserRepository userRepository;

    // username으로 UserEntity를 찾는 메서드
    public UserEntity findByUsername(String username) {
        UserEntity user = userRepository.findByUsername(username);
        //System.out.println("User found: " + user); // 디버깅 로그
        return user;
    }


    public byte[] getImageById(Long id) {
        return userRepository.findById(id)
                .map(UserEntity::getPhotoname) // 이미지 데이터 반환
                .orElse(null); // 사용자 없을 경우 null 반환
    }

    // username으로 프로필 이미지를 찾는 메서드
    public byte[] getImageByUsername(String username) {
        UserEntity user = userRepository.findByUsername(username);
        if (user != null) {
            return user.getPhotoname();
        }
        return null; // 사용자가 없거나 이미지가 없으면 null 반환
    }
}
