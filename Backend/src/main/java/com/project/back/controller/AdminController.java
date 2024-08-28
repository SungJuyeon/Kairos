package com.project.back.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller //이 클래스가 Spring MVC의 컨트롤러임을 나타낸다.
@ResponseBody   //모든 핸들러 메서드의 반환값이 HTTP 응답 본문으로 직접 쓰이도록 설정한다.
public class AdminController {
    @GetMapping("/admin")
    public String adminP() {
        return "Admin Controller";
    }
}
