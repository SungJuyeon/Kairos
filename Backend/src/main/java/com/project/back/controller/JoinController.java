package com.project.back.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.back.dto.JoinDTO;
import com.project.back.service.JoinService;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@AllArgsConstructor
public class JoinController {

    private final JoinService joinService;

    @PostMapping("/join")
    public ResponseEntity<String> joinProcess(
            @RequestParam("data") String data,
            @RequestParam(value = "file", required = false) MultipartFile file) {

        // 디버깅을 위해 data와 file 정보를 콘솔에 출력
        System.out.println("Received data: " + data);

        if (file != null && !file.isEmpty()) {
            System.out.println("Received file: " + file.getOriginalFilename());
            System.out.println("File size: " + file.getSize() + " bytes");
        } else {
            System.out.println("No file received");
        }

        try {
            // JSON 파싱
            JoinDTO joinDTO = new ObjectMapper().readValue(data, JoinDTO.class);

            if (joinDTO.getPassword() == null) {
                return ResponseEntity.badRequest().body("비밀번호를 입력해주세요");
            }

            if (file != null && !file.isEmpty()) {
                joinDTO.setPhotoname(file.getBytes());
            }

            joinService.joinProcess(joinDTO);
            return ResponseEntity.ok("회원가입 성공");

        } catch (IOException e) {
            return ResponseEntity.status(500).body("서버 오류: " + e.getMessage());
        }
    }


}

