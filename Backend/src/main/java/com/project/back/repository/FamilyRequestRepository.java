package com.project.back.repository;

import com.project.back.entity.FamilyRequest;
import com.project.back.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface FamilyRequestRepository extends JpaRepository<FamilyRequest, Long> {
    List<FamilyRequest> findBySender_Id(Long senderId);
    List<FamilyRequest> findByReceiver_Id(Long receiverId);




}