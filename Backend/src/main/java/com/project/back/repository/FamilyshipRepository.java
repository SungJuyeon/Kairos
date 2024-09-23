package com.project.back.repository;

import com.project.back.entity.Familyship;
import com.project.back.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface FamilyshipRepository extends JpaRepository<Familyship, Long> {

    @Query("SELECT f.user2 FROM Familyship f WHERE f.user1.id = :userId")
    List<UserEntity> findFamilyByUserId(@Param("userId") Long userId);

    @Query("SELECT CASE WHEN COUNT(f) > 0 THEN true ELSE false END FROM Familyship f WHERE (f.user1 = :user1 AND f.user2 = :user2) OR (f.user1 = :user2 AND f.user2 = :user1)")
    boolean existsFamilyship(@Param("user1") UserEntity user1, @Param("user2") UserEntity user2);

    List<Familyship> findByUser1Id(Long user1Id);
    List<Familyship> findByUser2Id(Long user2Id);
}
