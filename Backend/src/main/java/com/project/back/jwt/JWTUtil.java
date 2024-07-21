package com.project.back.jwt;
//JWT 생성, 검증

import java.nio.charset.StandardCharsets;
import java.util.Date;

import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import io.jsonwebtoken.Jwts;

@Component

public class JWTUtil {

    private final SecretKey secretKey; //JWT 토큰 객체 키를 저장할 시크릿 키
    //secretKey를 암호화
    public JWTUtil(@Value("${spring.jwtseretkey}") String secret) {
        this.secretKey = new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), Jwts.SIG.HS256.key().build().getAlgorithm()
        );
    }
    //JWT 내부를 파싱해 JWT 내부에 존재하는 username을 꺼내오는 것. (userRepository에서 가져오는 값은 DB에서 가져오는 값)
    //위변조된 키로 암호화된 JWT 검증할 경우 verifyWith에서 예외 발생
    public String getUsername(String token) {
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().get("username",String.class);
    }

    public String getRole(String token) {
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().get("role", String.class);
    }

    public String getCategory(String token) {
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().get("category",String.class);
    }

    public boolean isExpired(String token) {
        return Jwts.parser().verifyWith(secretKey).build().parseSignedClaims(token).getPayload().getExpiration().before(new Date());
    }

    //토큰 생성
    public String createJwt(String category,String username, String role, Long expiredMs) {
        return Jwts.builder()
                .claim("category",category) //category : access / refresh 구별
                .claim("username", username)
                .claim("role", role)
                .issuedAt(new Date(System.currentTimeMillis())) //현재 발행 시간
                .expiration(new Date(System.currentTimeMillis() + expiredMs))   //언제 소멸될 건지
                .signWith(secretKey)    //암호화 진행
                .compact();
    }
}
