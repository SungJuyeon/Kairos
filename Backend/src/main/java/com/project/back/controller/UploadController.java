package com.project.back.controller;

import com.project.back.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.http.ResponseEntity;
import org.springframework.ui.Model;
import org.springframework.stereotype.Controller;

import java.util.Base64;

@Controller
public class UploadController {

    @Autowired
    private UserService userService;

    @GetMapping("/getImage/{id}")
    public String getImage(@PathVariable Long id, Model model) {
        byte[] imageData = userService.getImageById(id); // 서비스에서 이미지 가져오기

        if (imageData != null) {
            String base64Image = Base64.getEncoder().encodeToString(imageData);
            model.addAttribute("image", "data:image/jpeg;base64," + base64Image); // Base64로 변환하여 모델에 추가
            return "image.html"; // image.html로 이동
        } else {
            return "error"; // 이미지가 없을 경우 에러 페이지로 이동
        }
    }
}