package com.project.back.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.project.back.entity.MemberEntity;
import com.project.back.service.LoginService;
import com.project.back.service.MemberService;

@RestController
@RequestMapping("/user")
public class UserController {
    private final MemberService memberService;
    private final LoginService loginService;

    public UserController(MemberService memberService, LoginService loginService) {
        this.memberService = memberService;
        this.loginService = loginService;
    }

    //내 계정 보기 loginId, email, name     OK
    @GetMapping
    public ResponseEntity<MemberEntity> getUserInfo(){
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        MemberEntity memberEntity = loginService.getUserInfo(email);
        return ResponseEntity.ok(memberEntity);
    }

    //email 정보로 name 변경    아직 오류
    @PutMapping("/update/name")
    public ResponseEntity<String> updateName(@RequestBody String newName){
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        memberService.updateName(email, newName);
        return ResponseEntity.ok("이름 변경 완료");
    }

    //email 정보로 pw 변경      아직 오류
    @PutMapping("/update/pw")
    public ResponseEntity<String> updatePw(@RequestBody String newPw){
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        memberService.updatePw(email, newPw);
        return ResponseEntity.ok("비밀번호 변경 완료");
    }
    
}
