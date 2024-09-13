package com.project.back.controller;

import com.project.back.dto.JoinDTO;
import com.project.back.service.JoinService;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController //RESTful 웹 서비스의 컨트롤러임을 나타낸다.
@AllArgsConstructor //생성자를 자동으로 생성한다.
public class JoinController {

    private final JoinService joinService;

    @PostMapping("/join")
    public ResponseEntity<String> joinProcess(@RequestBody JoinDTO joinDTO) {
        if (joinDTO.getPassword() == null) {
            return ResponseEntity.badRequest().body("비밀번호를 입력해주세요");
        }

        joinService.joinProcess(joinDTO);

        return ResponseEntity.ok("회원가입 성공");
    }
}
