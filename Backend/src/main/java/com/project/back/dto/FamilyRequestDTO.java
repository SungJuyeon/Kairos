package com.project.back.dto;

import lombok.Data;

@Data
public class FamilyRequestDTO {
    private String username;

    public FamilyRequestDTO() {
        // 기본 생성자
    }

    public FamilyRequestDTO(String username) {
        this.username = username;
    }
}
