package com.project.back.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.project.back.entity.MemberEntity;
import com.project.back.service.MemberService;

@RestController
public class HomeController {

    private final MemberService memberService;

    public HomeController(MemberService memberService) {
        this.memberService = memberService;
    }

    @GetMapping("/home")
    public ResponseEntity<String> home() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication != null && authentication.isAuthenticated()) {
            String loginId = authentication.getName();
            MemberEntity member = memberService.findByLoginId(loginId);

            if (member != null) {
                String email = member.getEmail(); // 사용자 이메일 가져오기
                String name = member.getName(); // 사용자 이름 가져오기

                String response = "Welcome, " + name + "!\n" +
                                  "<p>Email: " + email + "</p>";
                return ResponseEntity.ok(response);
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND).body("User not found");
            }
        } else {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Please log in to access this page.");
        }
    }
}
