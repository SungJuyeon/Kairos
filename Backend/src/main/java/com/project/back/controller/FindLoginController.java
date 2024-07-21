package com.project.back.controller;

import com.project.back.service.FindPasswordService;
import com.project.back.service.FindUsernameService;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@AllArgsConstructor
public class FindLoginController {
    private final FindUsernameService findUsernameService;
    private final FindPasswordService findPasswordService;

    @GetMapping("/find/username")
    public String findUsernameByEmail(@RequestParam String email) {
        return findUsernameService.findUsernameByEmail(email);
    }

    @PostMapping("/find/password")
    public String findPassword(@RequestParam String username, @RequestParam String email) {
        return findPasswordService.findPassword(username, email);
    }
}
