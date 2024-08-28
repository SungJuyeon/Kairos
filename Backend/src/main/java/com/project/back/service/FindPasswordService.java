package com.project.back.service;

import com.project.back.entity.UserEntity;
import com.project.back.repository.UserRepository;
import lombok.AllArgsConstructor;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
public class FindPasswordService {

    private final UserRepository userRepository;
    private final BCryptPasswordEncoder bCryptPasswordEncoder;

    public String findPassword(String username, String email) {
        UserEntity user = userRepository.findByUsername(username);
        if (user != null && user.getEmail().equals(email)) {
            return user.getPassword();  // 실제 서비스에서는 비밀번호를 직접 반환하지 않음
            //비밀번호 재설정 링크를 이메일로 보내는 방법
        }
        return null;  // 또는 사용자에게 적절한 메시지 반환
    }
}
