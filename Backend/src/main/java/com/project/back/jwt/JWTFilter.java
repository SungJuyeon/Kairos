package com.project.back.jwt;

import java.io.IOException;
import java.io.PrintWriter;

import com.project.back.dto.CustomUserDetails;
import com.project.back.entity.UserEntity;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;


import io.jsonwebtoken.ExpiredJwtException;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
//프론트의 API Client로 서버측에 요청을 보낸 후 데이터 획득
//Access token을 요청 헤더에 첨부하는데 access token 검증을 서버측 JWTFilter에 의해 진행
//Access token 만료된 경우 상태, 메시지 응답
@RequiredArgsConstructor
public class JWTFilter extends OncePerRequestFilter {
    private final JWTUtil jwtUtil;

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {

        //헤더에서 access키에 담긴 토큰을 꺼냄
        String accessToken = request.getHeader("access");

        //토큰이 없는 경우
        if (accessToken == null) {
            filterChain.doFilter(request, response);    //권한이 필요없는 경우도 있으니 다음 filter로 넘김
            return;
        }

        //토큰 만료 여부 확인
        try {
            jwtUtil.isExpired(accessToken);
        } catch (ExpiredJwtException e) {
            //response body

            PrintWriter writer = response.getWriter();
            writer.println("access token expired");

            //response status code
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);    //만료시 다음 filter로 넘기지 않음
            return;
            // 토큰 유무 검사와 달리 만료시에는 응답을 넘기지 않고 바로 상태코드 반환
        }

        //토큰이 access인지 확인 (발급시 payload에 명시)
        String category = jwtUtil.getCategory(accessToken);

        if (!category.equals("access")) {

            //response body
            PrintWriter writer = response.getWriter();
            writer.println("invaild access token");

            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            //프론트에서 400 응답을 달라고 요청하면 400을 주고 프론트 측에서 만료된 토큰을 가지고 refresh 코드를 주어 재발급할 수 있도록 특정 상태코드와 메시지 주기
            return;
        }
        // 여기 까지 오면 토큰 검증 완료

        //username, role 값을 획득 - 임시 세션 부분
        String username = jwtUtil.getUsername(accessToken);
        String role = jwtUtil.getRole(accessToken);

        UserEntity userEntity = new UserEntity();
        userEntity.setUsername(username);
        userEntity.setRole(role);
        CustomUserDetails customUserDetails = new CustomUserDetails(userEntity);
        //UsernamePasswordAuthenticationToken에 넣어 로그인 진행
        Authentication authToken = new UsernamePasswordAuthenticationToken(customUserDetails, null, customUserDetails.getAuthorities());
        //SecurityContextHolder에 해당 유저 정보를 넣어 일시적 세션 만들어짐
        SecurityContextHolder.getContext().setAuthentication(authToken);

        filterChain.doFilter(request,response);
    }
}
