
package com.project.back.service;

import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service 
@RequiredArgsConstructor //controller와 같이, final 멤버변수 생성자를 만드는 역할
public class MemberService {
    private final MemberRepository memberRepository;
    private final BCryptPasswordEncoder pwEncoder;

    //loginId 로 계정 찾기
    @Transactional(readOnly = true)
    public MemberEntity findByLoginId(String loginId) {
        return memberRepository.findByLoginId(loginId);
    }

    //Id로 계정 찾기
    public MemberEntity findById(String name, String email){
        return memberRepository.findByEmail(email)
        .filter(u -> u.getName().equals(name))
        .orElse(null);
    }

    //pw 찾기
    public MemberEntity findPw(String loginId, String name, String email){
        return memberRepository.findByLoginId(loginId);
        // .filter(m -> m.getName().equals(name))
        // .filter(m -> m.getEmail().equals(email))
    }

    //name 변경
    public String updateName(Long id, String name){
        MemberEntity member = memberRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("존재하지 않는 계정입니다."));
        member.updateName(name);
        return member.getName();
    }

    //pw 변경
    public String updatePw(Long id, String newPw){
        MemberEntity member = memberRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("존재하지 않는 계정입니다."));
        return member.updatePw(pwEncoder.encode(newPw));
    }

    public boolean validateUser(String loginId, String password) {
        MemberEntity member = memberRepository.findByLoginId(loginId);

        // 사용자 정보가 없거나, 비밀번호가 일치하지 않으면 인증 실패
        if (member == null || !member.getPw().equals(password)) {
            return false;
        }
        return true;
    }

    //id로 계정 정보 리턴
    public MemberEntity findById(Long userId){
        Optional<MemberEntity> OpMember = memberRepository.findById(userId);
        if(OpMember.isPresent()){
            MemberEntity member = OpMember.get();
            return member;
        }else{
            return null;
        }
    }

    public List<MemberEntity> findAll() {
        return memberRepository.findAll();
    }
}
