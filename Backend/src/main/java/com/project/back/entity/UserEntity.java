package com.project.back.entity;

//회원 저장 객체
//DB Table 이름 : userEntity

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Data;

@Entity
@Data
public class UserEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;

    private String username;    // = loginId

    private String password;

    private String role;

    //private String email;
    //private String name;
}
