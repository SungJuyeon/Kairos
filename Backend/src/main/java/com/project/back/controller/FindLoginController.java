package com.project.back.controller;

import com.project.back.service.FindPasswordService;
import com.project.back.service.FindUsernameService;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
//아이디와 비밀번호를 찾는 컨트롤러
@RestController
@AllArgsConstructor
public class FindLoginController {
    private final FindUsernameService findUsernameService;
    private final FindPasswordService findPasswordService;

    //이메일로 찾음
    @GetMapping("/find/username")
    public String findUsernameByEmail(@RequestParam String email) {
        return findUsernameService.findUsernameByEmail(email);
    }

    //username과 email로 찾음 -> 나중에 email로 확인 코드 보내는 걸로 바꾸기
    @PostMapping("/find/password")
    public String findPassword(@RequestParam String username, @RequestParam String email) {
        return findPasswordService.findPassword(username, email);
    }
}
