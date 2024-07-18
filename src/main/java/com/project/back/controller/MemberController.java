package com.project.back.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.project.back.dto.MemberFindDto;
import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;
import com.project.back.service.LoginService;
import com.project.back.service.MemberService;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;

@RestController
@RequiredArgsConstructor
public class MemberController {

    private static final Logger log = LoggerFactory.getLogger(MemberController.class);

    private final MemberService memberService;
    private final MemberRepository memberRepository;
    private final LoginService loginService;

    @PostMapping("/find/id")    //name, email로 loginId 찾기
    public ResponseEntity<?> findId(HttpServletRequest request, @RequestBody MemberFindDto member) {
        MemberEntity memberEntity = memberService.findById(member.getName(), member.getEmail());
        if (memberEntity == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("해당하는 이름 또는 email이 없습니다.");
        } else {
            return ResponseEntity.ok(memberEntity.getLoginId());
        }
    }

    @PostMapping("/find/pw")    //name, email로 pw 찾기
    public ResponseEntity<?> findPw(HttpServletRequest request, @RequestBody MemberFindDto member) {
        MemberEntity memberEntity = memberService.findById(member.getName(), member.getEmail());
        if (memberEntity == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("해당하는 이름 또는 email이 없습니다.");
        } else {
            return ResponseEntity.ok(memberEntity.getPw());
        }
    }

    // @GetMapping("/members")
    // public ResponseEntity<List<MemberEntity>> findAll(){
    //     List<MemberEntity> members = memberService.findAll();
    //     return ResponseEntity.ok(members);
    // }
}
