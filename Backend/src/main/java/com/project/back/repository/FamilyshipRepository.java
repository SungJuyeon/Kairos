package com.project.back.repository;

import com.project.back.entity.Familyship;
import com.project.back.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface FamilyshipRepository extends JpaRepository<Familyship, Long> {
    boolean existsByUser1AndUser2(UserEntity user1, UserEntity user2);

    @Query("SELECT f.user2 FROM Familyship f WHERE f.user1.id = :userId " +
            "UNION " +
            "SELECT f.user1 FROM Familyship f WHERE f.user2.id = :userId")
    List<UserEntity> findFamilyByUserId(@Param("userId") Long userId);
}
