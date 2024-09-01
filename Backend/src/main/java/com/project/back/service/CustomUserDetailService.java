package com.project.back.service;

import com.project.back.dto.CustomUserDetails;
import com.project.back.entity.UserEntity;
import com.project.back.repository.UserRepository;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;


import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class CustomUserDetailService implements UserDetailsService {
    private final UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        UserEntity userData = userRepository.findByUsername(username);  //조회
        if (username != null) { //데이터베이스에 username과 일치하는 사용자가 없을 경우
            return new CustomUserDetails(userData);
        }else {
            throw new UsernameNotFoundException("User not found with username: " + username);
        }
    }


}
