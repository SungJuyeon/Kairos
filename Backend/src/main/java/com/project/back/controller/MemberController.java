package com.project.back.controller;

import com.project.back.dto.MemberFindDto;
import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;
import com.project.back.service.LoginService;
import com.project.back.service.MemberService;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class MemberController {

    private static final Logger log = LoggerFactory.getLogger(MemberController.class);

    private final MemberService memberService;
    private final MemberRepository memberRepository;
    private final LoginService loginService;

    @PostMapping("/verify/id")
    public ResponseEntity<?> verifyId(HttpServletRequest request, @RequestBody @Validated MemberFindDto member) {
        boolean isDuplicate = memberRepository.existsByLoginId(member.getLoginId());
        if (isDuplicate) {
            log.error("중복 아이디 존재 = {}", member.getLoginId());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("이미 ID가 존재합니다.");
        } else {
            log.info("사용 가능한 아이디 = {}", member.getLoginId());
            return ResponseEntity.ok("ID 사용 가능");
        }
    }

    @PostMapping("/find/id")
    public ResponseEntity<?> findId(HttpServletRequest request, @RequestBody @Validated MemberFindDto member) {
        MemberEntity memberEntity = memberService.findById(member.getName(), member.getEmail());
        if (memberEntity == null) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("해당 이름과 email 없음");
        } else {
            log.info("이름과 email로 찾은 loginId = {}", memberEntity.getLoginId());
            return ResponseEntity.ok(memberEntity.getLoginId());
        }
    }

    // Add this to your MemberController class

    @PostMapping("/find/pw")
    public ResponseEntity<?> findPw(@RequestBody @Validated MemberFindDto member) {
        MemberEntity memberEntity = memberService.findById(member.getName(), member.getEmail());
        if (memberEntity == null) {
            log.error("해당 이름과 email 없음");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("해당 이름과 email 없음");
        } else {
            log.info("이름과 email로 찾은 password = {}", memberEntity.getPw());
            return ResponseEntity.ok(memberEntity.getPw());
        }
    }


    @GetMapping("/members")
    public ResponseEntity<List<MemberEntity>> findAll(){
        List<MemberEntity> members = memberService.findAll();
        return ResponseEntity.ok(members);
    }
}
