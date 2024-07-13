package com.project.back.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.project.back.entity.MemberEntity;

@Repository
public interface MemberRepository extends JpaRepository<MemberEntity, Long> {
    Optional<MemberEntity> findById(Long id);   //id로 찾기인데 id쓸 일이 없을 듯. 나중에 지우고
    MemberEntity findByName(String name);       //name으로 찾기
    Optional<MemberEntity> findByEmail(String email);   //email로 찾기 -> 회원가입 시 email 확인 코드 보내고 pw 찾기 시 email로 코드 보내기 나중에 구현
    MemberEntity findByLoginId(String loginId);     //loginId로 찾기

    boolean existsByLoginId(String loginId);    //loginId 존재하는지 확인
    boolean existsByEmail(String email);    //email 존재하는지 확인

}