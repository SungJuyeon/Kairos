package com.project.back.service;

import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Service;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
public class LogoutService {
    //@Override
    public void logout(HttpServletRequest request, HttpServletResponse response, Authentication authentication) {
        
    }
}
