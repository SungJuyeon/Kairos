package com.project.back.controller;

import com.project.back.entity.UserEntity;
import com.project.back.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
@ResponseBody
public class MainController {

    @Autowired
    private UserService userService;

    @GetMapping("/main")
    public String mainP() {
        // 현재 로그인된 사용자 이름 (username)
        String username = SecurityContextHolder.getContext().getAuthentication().getName();

        // 현재 로그인된 사용자 정보 가져오기
        UserEntity userEntity = userService.findByUsername(username);

        if (userEntity == null) {
            return "User not found";
        }

        return "Main Controller: " + username + ", Role: " + userEntity.getRole();
    }

    @GetMapping("/user/username")
    public String getUsername() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication != null && authentication.getPrincipal() instanceof UserDetails) {
            String username = ((UserDetails) authentication.getPrincipal()).getUsername();
            return username;
        } else {
            return "No authentication found";
        }
    }


    @GetMapping("/user/email")
    public String getEmail() {
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        System.out.println("Username from token: " + username); // 로그 추가
        UserEntity userEntity = userService.findByUsername(username);

        if (userEntity != null) {
            return userEntity.getEmail();
        } else {
            return "User not found";
        }
    }


    @GetMapping("/user/nickname")
    public String getNickname() {
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        UserEntity userEntity = userService.findByUsername(username);

        if (userEntity != null) {
            return userEntity.getNickname();
        } else {
            return "User not found";
        }
    }

    @GetMapping("/user/photo")
    public byte[] getPhoto() {
        String username = SecurityContextHolder.getContext().getAuthentication().getName();
        return userService.getImageByUsername(username);
    }
}
