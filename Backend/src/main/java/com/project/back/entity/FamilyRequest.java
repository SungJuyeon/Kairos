package com.project.back.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Data
public class FamilyRequest {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "sender_id")
    private UserEntity sender;

    @ManyToOne
    @JoinColumn(name = "receiver_id")
    private UserEntity receiver;

    @Enumerated(EnumType.STRING)
    private FamilyRequestStatus status;

    public enum FamilyRequestStatus {
        PENDING, ACCEPTED, REJECTED
    }
}