package com.project.back.controller;

import com.project.back.dto.JoinDTO;
import com.project.back.service.JoinService;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController //RESTful 웹 서비스의 컨트롤러임을 나타낸다.
@AllArgsConstructor //생성자를 자동으로 생성한다.
public class JoinController {

    private final JoinService joinService;

    @PostMapping("/join")
    public String joinProcess(JoinDTO joinDTO) {
        if (joinDTO.getPassword() == null) {
            return "비밀번호가 맞지 않습니다.";
        }
        joinService.joinProcess(joinDTO);

        return "회원가입 성공";
    }
}
