package com.project.back.jwt;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Collection;
import java.util.Date;
import java.util.Iterator;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.project.back.dto.LoginDTO;
import com.project.back.entity.RefreshEntity;
import com.project.back.repository.RefreshRepository;
import jakarta.servlet.ServletInputStream;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;


import jakarta.servlet.FilterChain;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.util.StreamUtils;

////컨트롤러단에서 로그인을 구현하려면 현재 등록한 LoginFilter를 등록하지 않으면 POST : /login 경로까지 요청이 넘어온다.
//SecurityConfig에서 formLogin 방식 disable 했기 때문에 UsernamePasswordAuthenticationFilter custom 필요
//LoginFilter는 UsernamePasswordAuthenticationFilter를 상속 받아서 구현하였는데 이 필터가 POST : /login에서만 반응하도록 설정되어 있음
//  엔드포인트 : "/login"
@RequiredArgsConstructor
public class LoginFilter extends UsernamePasswordAuthenticationFilter {

    private final AuthenticationManager authenticationManager;
    private final JWTUtil jwtUtil;
    private final RefreshRepository refreshRepository;
    //클라이언트로부터 받은 username과 password를 추출하여 UsernamePasswordAuthenticationToken 객체를 생성
    @Override
    public Authentication attemptAuthentication(HttpServletRequest request, HttpServletResponse response) throws AuthenticationException {
        //client 요청의 username, password 추출
        //multipart/form-data 형식
//        String username = obtainUsername(request);  //=loginId
//        String password = obtainPassword(request);

        LoginDTO loginDTO = new LoginDTO();

        try {
            ObjectMapper objectMapper = new ObjectMapper();
            ServletInputStream inputStream = request.getInputStream();
            String messageBody = StreamUtils.copyToString(inputStream, StandardCharsets.UTF_8);
            loginDTO = objectMapper.readValue(messageBody, LoginDTO.class);

        } catch (IOException e) {
            throw new RuntimeException(e);
        }

        String username = loginDTO.getUsername();
        String password = loginDTO.getPassword();

        //UsernamePasswordAuthentication 이 authenticationManager 에게 username,password 를 전달 ( 토큰 )
        // null 값은 role 자리 임시
        UsernamePasswordAuthenticationToken usernamePasswordAuthenticationToken = new UsernamePasswordAuthenticationToken(username,password,null);
        //AuthenticationManager를 사용하여 인증을 시도
        return authenticationManager.authenticate(usernamePasswordAuthenticationToken);
    }
    //로그인 성공했을 시 이 메서드가 실행됨
    @Override
    protected void successfulAuthentication(HttpServletRequest request, HttpServletResponse response, FilterChain chain, Authentication authentication) {

        String username = authentication.getName(); //username 가져옴

        Collection<? extends GrantedAuthority> authorities = authentication.getAuthorities();
        Iterator<? extends GrantedAuthority> iterator = authorities.iterator();
        GrantedAuthority auth = iterator.next();

        String role = auth.getAuthority();  //role 값 가져옴
        //토큰 생성
        String access = jwtUtil.createJwt("access", username, role, 600000L);   //username, role, token시간 - 10분
        String refresh = jwtUtil.createJwt("refresh", username, role, 86400000L);   //24시간
        //Refresh 토큰 저장
        addRefreshEntity(username,refresh,86400000L);
        //응답 설정
        response.setHeader("access", access);   //응답 헤더에 access token을 access key에 넣어줌
        response.addCookie(createCookie("refresh",refresh));    //응답 cookie에 refresh token을 넣어줌
        response.setStatus(HttpStatus.OK.value());  //응답 상태 코드 200
    }

    //successfulAuthentication에서 token이 저장될 수 있도록 하는 함수
    private void addRefreshEntity(String username, String refresh, Long expiredMs) {

        Date date = new Date(System.currentTimeMillis() + expiredMs);   //만료일

        RefreshEntity refreshEntity = new RefreshEntity();
        refreshEntity.setUsername(username);
        refreshEntity.setRefresh(refresh);
        refreshEntity.setExpiration(date.toString());

        refreshRepository.save(refreshEntity);  //해당 token 저장
    }
    //cookie 생성   key 값 , jwt 값이 들어갈 value
    private Cookie createCookie(String key, String value) {
        Cookie cookie = new Cookie(key, value);
        cookie.setMaxAge(24 * 60 * 60);
        cookie.setSecure(true);
        cookie.setPath("/");    //cookie 적용 범위
        cookie.setHttpOnly(true);

        return cookie;
    }
    //로그인 실패 시 동작하는 메서드
    @Override
    protected void unsuccessfulAuthentication(HttpServletRequest request, HttpServletResponse response, AuthenticationException failed) {
        response.setStatus(401);
        System.out.println("로그인 실패");
    }
}
