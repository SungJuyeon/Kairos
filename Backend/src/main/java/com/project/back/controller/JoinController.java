package com.project.back.controller;

import com.project.back.dto.JoinDTO;
import com.project.back.service.JoinService;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@AllArgsConstructor
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
