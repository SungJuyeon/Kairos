package com.project.back.dto;

import lombok.Data;

@Data
public class FamilyRequestDTO {
    private Long requestId;
    private String senderUsername;  // This should be the sender's username
    private String receiverUsername; // This should be the receiver's username
    private String status;

    public FamilyRequestDTO() {}

    public FamilyRequestDTO(Long requestId, String senderUsername, String receiverUsername, String status) {
        this.requestId = requestId;
        this.senderUsername = senderUsername;
        this.receiverUsername = receiverUsername;
        this.status = status;
    }
}
