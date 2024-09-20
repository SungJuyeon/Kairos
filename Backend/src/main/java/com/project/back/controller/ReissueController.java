package com.project.back.controller;

import java.util.Date;

import com.project.back.entity.RefreshEntity;
import com.project.back.jwt.JWTUtil;
import com.project.back.repository.RefreshRepository;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;


import io.jsonwebtoken.ExpiredJwtException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
//서버에서 refresh token을 받으면 검증하고, 새 access token을 재발급하는 로직
//= JWT를 받고, 검증하고, 새로운 JWT를 발급
//  http://localhost:8080/reissue
//프론트에서 credential true 설정하면 자동으로 쿠키가 헤더에 탑재되어 서버측으로 전송된다.
@RestController
@RequiredArgsConstructor
public class ReissueController {
    private final JWTUtil jwtUtil;

    private final RefreshRepository refreshRepository;

    @PostMapping("/reissue")
    public ResponseEntity<?> resissue(HttpServletRequest request, HttpServletResponse response) {

        String refresh = null;  //요청의 cookie에서 가져와야함
        Cookie[] cookies = request.getCookies();
        for (Cookie cookie : cookies) {
            //cookie에 refresh 값이 있다면 저장
            if (cookie.getName().equals("refresh")) {
                refresh = cookie.getValue();
            }
        }
        //refresh token이 없는 경우
        if (refresh == null) {
            return new ResponseEntity<>("refresh token null", HttpStatus.BAD_REQUEST);
        }

        //만료 여부 확인
        try{
            jwtUtil.isExpired(refresh);
        }catch(ExpiredJwtException e){

            //response status code
            return new ResponseEntity<>("refresh token expired", HttpStatus.BAD_REQUEST);
        }

        //token이 refresh 인지 확인 ( 발급시 페이로드에 명시 )
        String category = jwtUtil.getCategory(refresh); //getCategory는 token을 받으면 token의 payload에 담겨있는 category값을 꺼냄
        if (!category.equals("refresh")) {  //category값이 refresh가 아닌 경우
            return new ResponseEntity<>("invalid refresh token", HttpStatus.BAD_REQUEST);
        }

        //DB에 저장 되어 있는지 확인
        Boolean isExist = refreshRepository.existsByRefresh(refresh);
        if (!isExist) {
            return new ResponseEntity<>("invalid refresh token", HttpStatus.BAD_REQUEST);
        }

        String username = jwtUtil.getUsername(refresh);
        String role = jwtUtil.getRole(refresh);

        //새 JWT 생성
        String newAccess = jwtUtil.createJwt("access", username, role, 6000000L);
        String newRefresh = jwtUtil.createJwt("refresh", username, role, 86400000L);    //refresh rotate

        //Refresh 토큰 저장 DB에 기존의 Refresh 토큰 삭제 후 새 Refresh 토큰 저장
        refreshRepository.deleteByRefresh(refresh);
        addRefreshEntity(username, newRefresh, 86400000L);

        //새 token을 응답으로 보냄
        response.setHeader("access", newAccess);
        response.addCookie(createCookie("refresh",newRefresh)); //refresh는 cookie로 응답함

        return new ResponseEntity<>(HttpStatus.OK);
    }

    private void addRefreshEntity(String username, String refresh, long expiredMs) {
        Date date = new Date(System.currentTimeMillis() + expiredMs);

        RefreshEntity refreshEntity = new RefreshEntity();

        refreshEntity.setUsername(username);
        refreshEntity.setRefresh(refresh);
        refreshEntity.setExpiration(date.toString());

        refreshRepository.save(refreshEntity);
    }

    private Cookie createCookie(String key, String value) {
        Cookie cookie = new Cookie(key, value);
        cookie.setMaxAge(24 * 60 * 60);
        cookie.setSecure(true);
        cookie.setHttpOnly(true);   //임베드 공격 방지

        return cookie;
    }


}
