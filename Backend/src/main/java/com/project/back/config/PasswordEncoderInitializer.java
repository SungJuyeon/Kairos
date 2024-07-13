package com.project.back.config;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.project.back.service.PasswordEncoderService;

import jakarta.annotation.PostConstruct;

@Component
public class PasswordEncoderInitializer {

    @Autowired
    private PasswordEncoderService passwordEncoderService;

    @PostConstruct
    public void init() {
        passwordEncoderService.encodePasswords();
    }
}
