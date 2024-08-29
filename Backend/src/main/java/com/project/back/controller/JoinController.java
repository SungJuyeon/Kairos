package com.project.back.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.back.dto.JoinDTO;
import com.project.back.service.JoinService;
import lombok.AllArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

@RestController
@AllArgsConstructor
public class JoinController {

    private final JoinService joinService;
    private static final Logger logger = LoggerFactory.getLogger(JoinController.class);

    @PostMapping("/join")
    public ResponseEntity<String> joinProcess(
            @RequestParam("data") String data,
            @RequestParam("file") MultipartFile file) throws IOException {

        // 요청 파라미터 로그 출력
        logger.debug("Received data: {}", data);
        if (file != null) {
            logger.debug("Received file: {}", file.getOriginalFilename());
        } else {
            logger.debug("No file received");
        }

        // JSON 파싱
        JoinDTO joinDTO = new ObjectMapper().readValue(data, JoinDTO.class);

        if (joinDTO.getPassword() == null) {
            return ResponseEntity.badRequest().body("비밀번호를 입력해주세요");
        }

        if (file != null && !file.isEmpty()) {
            joinDTO.setPhotoname(file);
        }

        // 파일 처리 로직 추가
        joinService.joinProcess(joinDTO);
        return ResponseEntity.ok("회원가입 성공");
    }
}
