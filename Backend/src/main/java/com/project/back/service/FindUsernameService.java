package com.project.back.service;

import com.project.back.entity.UserEntity;
import com.project.back.repository.UserRepository;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class FindUsernameService {

    private final UserRepository userRepository;

    public String findUsernameByEmail(String email) {
        UserEntity user = userRepository.findByEmail(email);
        if (user != null) {
            return user.getUsername();
        }
        return null;  // 또는 사용자에게 적절한 메시지 반환
    }
}