package com.project.back.dto;


import lombok.Data;
import org.springframework.web.multipart.MultipartFile;

@Data
public class JoinDTO {
    private String username;    //= login id
    private String password;
    private String email;
    private String nickname;
    private byte[] photoname; // 파일 데이터
}
