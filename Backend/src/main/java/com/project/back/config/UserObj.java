package com.project.back.config;

import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public class UserObj implements UserDetailsService{
    private final MemberRepository memberRepository;

    public UserObj(MemberRepository memberRepository) {
        this.memberRepository = memberRepository;
    }

    @Override
    public UserDetails loadUserByUsername(String loginId) throws UsernameNotFoundException {
        System.out.println("전달된 아이디: " + loginId);
        if (loginId == null || loginId.trim().isEmpty()) {
            System.out.println("아이디 null이거나 빈 문자열입니다.");
            throw new UsernameNotFoundException("아이디 null이거나 빈 문자열입니다.");
        }
    
        Optional<MemberEntity> user = memberRepository.findByEmail(loginId);
        if (user == null) {
            System.out.println("아이디로 사용자를 찾을 수 없습니다: " + loginId);
            throw new UsernameNotFoundException(loginId);
        }
        return null;
    }
}
