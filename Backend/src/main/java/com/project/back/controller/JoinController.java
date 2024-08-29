package com.project.back.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.back.dto.JoinDTO;
import com.project.back.entity.UserEntity;
import com.project.back.service.JoinService;
import lombok.AllArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.Base64;

@RestController //RESTful 웹 서비스의 컨트롤러임을 나타낸다.
@AllArgsConstructor //생성자를 자동으로 생성한다.
public class JoinController {

    private final JoinService joinService;

    @PostMapping("/join")
    public ResponseEntity<String> joinProcess(
            @RequestParam("data") String data,
            @RequestParam("file") MultipartFile file) throws IOException {

        // JSON 파싱
        JoinDTO joinDTO = new ObjectMapper().readValue(data, JoinDTO.class);

        if (joinDTO.getPassword() == null) {
            return ResponseEntity.badRequest().body("비밀번호를 입력해주세요");
        }

        if (file != null && !file.isEmpty()) {
            joinDTO.setPhotoname(file.getBytes());
        }

        // 파일 처리 로직 추가
        // 예: 파일 저장

        joinService.joinProcess(joinDTO);
        return ResponseEntity.ok("회원가입 성공");


    }


//    @PostMapping("/join")
//    public ResponseEntity<String> joinProcess(@RequestBody JoinDTO joinDTO) {
//        if (joinDTO.getPassword() == null) {
//            return ResponseEntity.badRequest().body("비밀번호를 입력해주세요");
//        }
//
//
//        joinService.joinProcess(joinDTO);
//        return ResponseEntity.ok("회원가입 성공");
//    }


}
