package com.project.back.repository;

import com.project.back.entity.RefreshEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.transaction.annotation.Transactional;


public interface RefreshRepository extends JpaRepository<RefreshEntity,Long> {
    Boolean existsByRefresh(String refresh);    //refresh token이 존재하는지

    @Transactional
    void deleteByRefresh(String refresh);
}
