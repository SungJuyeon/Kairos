package com.project.back.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Setter
@Getter
@AllArgsConstructor
@NoArgsConstructor
@Builder
@Table(name = "member")   //database에 해당 이름의 테이블 생성
public class MemberEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "loginId")   //자동으로 변환하지 않게
    private String loginId;

    @Column(name = "name")
    private String name;

    @Column(name = "email")
    private String email;

    @Column(name = "pw")
    private String pw;


    public boolean isPresent() {
        return true;
    }
	public String updateName(String name) {
        this.name = name;
        return name;
    }
    public String updatePw(String newPw) {
        this.pw = newPw;
        return newPw;
    }
    public MemberEntity(String loginId, String pw) {
        this.loginId = loginId;
        this.pw = pw;
    }
}
