//DB 테이블을 조회

package com.project.back.repository;

import com.project.back.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<UserEntity,Long> {
    Boolean existsByUsername(String username);  //회원가입 시 username 여부 확인

    UserEntity findByUsername(String username); //DB에서 회원을 조회

}
