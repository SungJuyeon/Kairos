package com.project.back.dto;

import lombok.Data;

@Data
public class FamilyUserDTO {
    private String nickname;
    private byte[] photoname;

    public FamilyUserDTO(String nickname, byte[] photoname) {
        this.nickname = nickname;
        this.photoname = photoname;
    }
}
