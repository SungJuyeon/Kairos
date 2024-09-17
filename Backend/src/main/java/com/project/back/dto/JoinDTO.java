package com.project.back.dto;


import lombok.Data;

@Data
public class JoinDTO {
    private String username;    //= login id
    private String password;
    private String email;
    private String nickname;
    private byte[] photoname; // 파일 데이터
}
