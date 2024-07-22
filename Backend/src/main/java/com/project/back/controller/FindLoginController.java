package com.project.back.controller;

import com.project.back.dto.FindDTO;
import com.project.back.service.FindPasswordService;
import com.project.back.service.FindUsernameService;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@AllArgsConstructor
public class FindLoginController {
    private final FindUsernameService findUsernameService;
    private final FindPasswordService findPasswordService;
    @PostMapping("/find/username")
    public ResponseEntity<String> findUsernameByEmail(@RequestBody FindDTO findDTO) {
        String username = findUsernameService.findUsernameByEmail(findDTO.getEmail());
        if (username != null) {
            return ResponseEntity.ok(username);
        }
        return ResponseEntity.status(404).body("사용자를 찾을 수 없습니다.");
    }

    @PostMapping("/find/password")
    public ResponseEntity<String> findPassword(@RequestBody FindDTO findDTO) {
        String password = findPasswordService.findPassword(findDTO.getUsername(), findDTO.getEmail());
        if (password != null) {
            return ResponseEntity.ok(password);
        }
        return ResponseEntity.status(404).body("이메일 또는 사용자가 없습니다.");
    }
}
