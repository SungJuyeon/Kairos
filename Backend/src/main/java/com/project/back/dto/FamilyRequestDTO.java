package com.project.back.dto;

import lombok.Data;

@Data
public class FamilyRequestDTO {
    private Long requestId;
    private String senderUsername;
    private String status;

    public FamilyRequestDTO(Long requestId, String senderUsername, String status) {
        this.requestId = requestId;
        this.senderUsername = senderUsername;
        this.status = status;
    }
}
