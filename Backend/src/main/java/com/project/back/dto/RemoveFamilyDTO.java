package com.project.back.dto;

import lombok.Data;

@Data
public class RemoveFamilyDTO {
    private String memberUsername; // 삭제할 가족 회원의 username
}