package com.project.back.entity;

//토큰 저장소
//DB를 통해 refresh token을 저장

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Data;

@Entity
@Data
public class RefreshEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;    //하나의 username이 여러 개 token 가지는 것이 가능하기에 unique (X)
    private String refresh;
    private String expiration;

}
