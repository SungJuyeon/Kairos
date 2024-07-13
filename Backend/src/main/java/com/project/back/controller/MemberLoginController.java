
package com.project.back.controller;

import java.util.HashMap;
import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.project.back.entity.MemberEntity;
import com.project.back.service.LoginService;
import com.project.back.service.MemberService;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
@Slf4j
@RestController
@RequiredArgsConstructor
public class MemberLoginController {
    private final MemberService memberService;
    private final LoginService loginService;
    private BCryptPasswordEncoder encoder;

    @PostMapping("/login")
    public ResponseEntity<Map<String, String>> login(@RequestParam String loginId, @RequestParam String password,
    HttpServletRequest request) {
                
        Map<String, String> response = new HashMap<>();
        System.out.println("로그인 시도: loginId=" + loginId + ", pw=" + password);

        try {
            MemberEntity member = loginService.login(loginId, password);

            // 사용자 인증 성공
            HttpSession session = request.getSession();
            session.setAttribute(SessionConst.LOGIN_MEMBER, member);

            response.put("status", "success");
            response.put("sessionId", session.getId());
            return ResponseEntity.ok(response);
        } catch (AuthenticationException e) {
            // 사용자 인증 실패
            log.error("로그인 실패: {}", e.getMessage());
            response.put("status", "loginFail");
            response.put("message", "인증 실패");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
        } catch (Exception e) {
            // 기타 예외 처리
            log.error("로그인 오류: {}", e.getMessage());
            response.put("status", "error");
            response.put("message", "서버 오류");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }

    @PostMapping("/join")
    public ResponseEntity<String> join(@RequestBody MemberEntity member) {
        try {
            loginService.join(member);
            return ResponseEntity.ok().build();
        } catch (IllegalStateException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).build();
        }
    }

    @GetMapping("/logoutOk")
    public ResponseEntity<Void> logoutOk() {
        System.out.println("로그아웃 성공");
        return ResponseEntity.ok().build();
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout(HttpServletRequest request){
        HttpSession session = request.getSession(false);
        if(session != null) session.invalidate();
        return ResponseEntity.ok().build();
    }

    @GetMapping("/user")
    public ResponseEntity<MemberEntity> getUserPage() {
        String email = SecurityContextHolder.getContext().getAuthentication().getName();
        MemberEntity memberEntity = loginService.getUserInfo(email);
        return ResponseEntity.ok(memberEntity);
    }

}