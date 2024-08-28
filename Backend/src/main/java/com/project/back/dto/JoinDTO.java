package com.project.back.dto;


import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

@Data
public class JoinDTO {
    private String username;    //= login id
    private String password;
    private String email;
    private String nickname;
    private MultipartFile potoname; // 프로필 이미지 파일
}
