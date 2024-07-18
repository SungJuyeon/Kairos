package com.project.back.service;

import java.util.Optional;

import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.project.back.config.PasswordUtils;
import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;

@Transactional
@Service //spring이 관리해주는 객체
public class LoginService {
    private final MemberRepository memberRepository;
    private final BCryptPasswordEncoder pwEncoder;

    public LoginService(MemberRepository memberRepository, BCryptPasswordEncoder pwEncoder) {
        this.memberRepository = memberRepository;
        this.pwEncoder = pwEncoder;
    }

    //내 계정 정보 조회
    public MemberEntity getUserInfo(String email){
        Optional<MemberEntity> memberEntity = memberRepository.findByEmail(email);
        return memberEntity.orElse(null);
    }

    public MemberEntity login(String loginId, String password) {
        MemberEntity user = memberRepository.findByLoginId(loginId);
    
        if (user == null) {
            throw new UsernameNotFoundException("사용자 없음");
        }
    
        String storedPassword = user.getPw();
        boolean isBCrypt = PasswordUtils.isBCryptPassword(storedPassword);
        System.out.println("pw BCrypt: " + isBCrypt);
    
        if (!pwEncoder.matches(password, storedPassword)) {
            throw new BadCredentialsException("비밀번호 틀림");
        }
        return user;
    }

    public void join(MemberEntity member) {
        if (memberRepository.existsByLoginId(member.getLoginId())) {
            throw new IllegalStateException(member.getLoginId() + "은(는) 이미 존재하는 아이디입니다.");
        }
        if (memberRepository.existsByEmail(member.getEmail())) {
            throw new IllegalStateException(member.getEmail() + "은(는) 이미 존재하는 이메일입니다.");
        }
        // 비밀번호 암호화
        member.setPw(pwEncoder.encode(member.getPw()));
        // 회원 정보 저장
        memberRepository.save(member);
    }
}