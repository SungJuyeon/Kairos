package com.project.back.controller;

//post 방식으로 /loogin 으로 username, password 보내면 authentication에 token 정보 나오고,
// 이 값을 Get 방식으로 / 으로 요청을 보내면 일시적인 session 생성되어 볼 수 있음.

import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.Collection;
import java.util.Iterator;

@Controller
@ResponseBody
public class MainController {

    @GetMapping("/")
    public String mainP() {
        //현재 세션 세션 사용자 아이디
        String name = SecurityContextHolder.getContext().getAuthentication().getName();
//        JWT가 session을 stateless 한 채로 진행되긴 하지만 1회성에 한하여 과정 중에 잠시 세션이 생성되게 되는데 이때
//        JWTFilter를 통과한 뒤 세션을 확인하는 것이 가능하다.

        System.out.println(name);


        //현재 세션 사용자 role
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        Collection<? extends GrantedAuthority> authorities = authentication.getAuthorities();
        Iterator<? extends GrantedAuthority> iterator = authorities.iterator();
        GrantedAuthority authority = iterator.next();
        String role = authority.getAuthority();
        System.out.println(role);


        return "Main Controller " + name + role;

    }
}
