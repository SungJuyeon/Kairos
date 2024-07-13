
package com.project.back.repository;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.project.back.entity.MemberEntity;

public interface MemberRepository extends JpaRepository<MemberEntity, Long>{
    @SuppressWarnings("null")
    Optional<MemberEntity> findById(Long id);
    MemberEntity findByName(String name);
    Optional<MemberEntity> findByEmail(String email);
    MemberEntity findByLoginId(String loginId);

    boolean existsByLoginId(String loginId);
    boolean existsByEmail(String email);
}