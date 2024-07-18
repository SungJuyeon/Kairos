package com.project.back.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

import com.project.back.config.PasswordUtils;
import com.project.back.entity.MemberEntity;
import com.project.back.repository.MemberRepository;

@RestController
public class PasswordCheckController {

    @Autowired
    private MemberRepository memberRepository;
//pw를 BCrypt 암호화함
    @GetMapping("/check-password/{userId}")
    public String checkPasswordEncoding(@PathVariable Long userId) {
        MemberEntity user = memberRepository.findById(userId)
            .orElseThrow(() -> new IllegalArgumentException("Invalid loginId"));
        String storedPassword = user.getPw();

        boolean isBCrypt = PasswordUtils.isBCryptPassword(storedPassword);
        return isBCrypt ? "BCrypt encoded" : "not BCrypt encoded";
    }
}
