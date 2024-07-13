
package com.project.back.service;

import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import com.project.back.dto.AuthenticationResponse;
import com.project.back.dto.LoginRequestDto;
import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;

@Service
public class AuthService {

    @Autowired
    private MemberRepository userRepository;

    @Autowired
    private BCryptPasswordEncoder passwordEncoder;

    public AuthenticationResponse authenticate(LoginRequestDto loginRequest) {
        // 사용자 인증 로직 구현
        MemberEntity user = userRepository.findByName(loginRequest.getName());
        
        if (user != null && passwordEncoder.matches(loginRequest.getPassword(), user.getPw())) {
            // 비밀번호 일치 시 인증 성공 처리
            String sessionId = generateSessionId();
            // 세션 관리 로직 등...
            return new AuthenticationResponse(sessionId);
        } else {
            // 인증 실패 처리
            return null;
        }
    }

    // 세션 ID 생성 메서드 등 다양한 보안 관련 로직 포함
    private String generateSessionId() {
        // 세션 ID 생성 로직
        return UUID.randomUUID().toString();
    }
}
