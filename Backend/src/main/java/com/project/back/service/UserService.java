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

    public byte[] getImageById(Long id) {
        return userRepository.findById(id)
                .map(UserEntity::getPhotoname) // 이미지 데이터 반환
                .orElse(null); // 사용자 없을 경우 null 반환
    }

    public byte[] getImageByUsername(String username) {
        return userRepository.findImageByUsername(username); // 이미지 데이터 반환
    }
}