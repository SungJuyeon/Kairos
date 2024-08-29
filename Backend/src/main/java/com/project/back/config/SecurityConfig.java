package com.project.back.config;


import java.util.Collections;

import com.project.back.jwt.CustomLogoutFilter;
import com.project.back.jwt.JWTFilter;
import com.project.back.jwt.JWTUtil;
import com.project.back.jwt.LoginFilter;
import com.project.back.repository.RefreshRepository;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.security.web.authentication.logout.LogoutFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;

import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;

@Configuration
@EnableWebSecurity  //Configuration은 Security를 위한 configure이기 때문에 필요
@RequiredArgsConstructor
public class SecurityConfig {

    private final AuthenticationConfiguration authenticationConfiguration;
    private final JWTUtil jwtUtil;
    private final RefreshRepository refreshRepository;


    @Bean
    public BCryptPasswordEncoder bCryptPasswordEncoder() {  //암호화
        return new BCryptPasswordEncoder();
    }


    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration configuration)throws Exception {
        return configuration.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception{
        http
                .cors((cors) -> cors.configurationSource(new CorsConfigurationSource() {
                    @Override
                    public CorsConfiguration getCorsConfiguration(HttpServletRequest request) {

                        CorsConfiguration configuration = new CorsConfiguration();
                        configuration.setAllowedOrigins(Collections.singletonList("http://localhost:8081"));
                        configuration.setAllowedMethods(Collections.singletonList("*"));
                        configuration.setAllowCredentials(true);
                        configuration.setAllowedHeaders(Collections.singletonList("*"));
                        configuration.setMaxAge(3600L);

                        configuration.setExposedHeaders(Collections.singletonList("Authorization"));
                        return configuration;
                    }
                }));

        http
                .csrf((auth) -> auth.disable())     // JWT는 Session을 Stateless 방식으로 하기 때문에 csrf 구현이 필수 X

                .formLogin((auth)->auth.disable())      //http formLogin 방식 disable
                .httpBasic((auth) -> auth.disable());   //http basic 인증 방식 disable

        http
                .authorizeHttpRequests((auth) -> auth   //경로별 인가 작업
                        .requestMatchers("/login", "/", "/join", "/getImage/{id}", "/find/username", "find/password").permitAll()
                        .requestMatchers("/admin").hasRole("ADMIN")
                        .requestMatchers("/reissue").permitAll()        //모든 사용자는 access token 만료된 상태로 접근하기에 permitAll
                        .anyRequest().authenticated() //이외의 요청에는 인증이 필요
                );
        http.addFilterBefore(new CustomLogoutFilter(jwtUtil, refreshRepository), LogoutFilter.class);

        // 세션 설정하는 부분 : JWT는 무상태(STATELESS)로 설정
        http
                .sessionManagement((session) -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS));

        http
                .addFilterBefore(new JWTFilter(jwtUtil), LoginFilter.class);
        http
                .addFilterAt(new LoginFilter(authenticationManager(authenticationConfiguration),jwtUtil,refreshRepository), UsernamePasswordAuthenticationFilter.class);

        return http.build();

    }
}


//package com.project.back.config;
//
//
//import java.util.Collections;
//
//import com.project.back.jwt.CustomLogoutFilter;
//import com.project.back.jwt.JWTFilter;
//import com.project.back.jwt.JWTUtil;
//import com.project.back.jwt.LoginFilter;
//import com.project.back.repository.RefreshRepository;
//import org.springframework.context.annotation.Bean;
//import org.springframework.context.annotation.Configuration;
//import org.springframework.security.authentication.AuthenticationManager;
//import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
//import org.springframework.security.config.annotation.web.builders.HttpSecurity;
//import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
//import org.springframework.security.config.http.SessionCreationPolicy;
//import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
//import org.springframework.security.web.SecurityFilterChain;
//import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
//import org.springframework.security.web.authentication.logout.LogoutFilter;
//import org.springframework.web.cors.CorsConfiguration;
//import org.springframework.web.cors.CorsConfigurationSource;
//
//import jakarta.servlet.http.HttpServletRequest;
//import lombok.RequiredArgsConstructor;
//
//@Configuration
//@EnableWebSecurity  //Configuration은 Security를 위한 configure이기 때문에 필요
//@RequiredArgsConstructor
//public class SecurityConfig {
//
//    private final AuthenticationConfiguration authenticationConfiguration;
//    private final JWTUtil jwtUtil;
//    private final RefreshRepository refreshRepository;
//
//
//    @Bean
//    public BCryptPasswordEncoder bCryptPasswordEncoder() {  //암호화
//        return new BCryptPasswordEncoder();
//    }
//
//
//    @Bean
//    public AuthenticationManager authenticationManager(AuthenticationConfiguration configuration)throws Exception {
//        return configuration.getAuthenticationManager();
//    }
//
//    @Bean
//    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception{
//        http
//                .cors((cors) -> cors.configurationSource(new CorsConfigurationSource() {
//                    @Override
//                    public CorsConfiguration getCorsConfiguration(HttpServletRequest request) {
//
//                        CorsConfiguration configuration = new CorsConfiguration();
//                        configuration.setAllowedOrigins(Collections.singletonList("http://localhost:8081"));
//                        configuration.setAllowedMethods(Collections.singletonList("*"));
//                        configuration.setAllowCredentials(true);
//                        configuration.setAllowedHeaders(Collections.singletonList("*"));
//                        configuration.setMaxAge(3600L);
//
//                        configuration.setExposedHeaders(Collections.singletonList("Authorization"));
//                        return configuration;
//                    }
//                }));
//
//        http
//                .csrf((auth) -> auth.disable())     // JWT는 Session을 Stateless 방식으로 하기 때문에 csrf 구현이 필수 X
//
//                .formLogin((auth)->auth.disable())      //http formLogin 방식 disable
//                .httpBasic((auth) -> auth.disable());   //http basic 인증 방식 disable
//
//        http
//                .authorizeHttpRequests(auth -> auth
//                        .requestMatchers("/login", "/", "/join", "/find/username", "/find/password").permitAll()
//                        .requestMatchers("/admin").hasRole("ADMIN")
//                        .requestMatchers("/reissue").permitAll()
//                        .anyRequest().authenticated());
//
//        http.addFilterBefore(new CustomLogoutFilter(jwtUtil, refreshRepository), LogoutFilter.class);
//
//        // 세션 설정하는 부분 : JWT는 무상태(STATELESS)로 설정
//        http
//                .sessionManagement((session) -> session
//                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS));
//
//        http
//                .addFilterBefore(new JWTFilter(jwtUtil), LoginFilter.class);
//        http
//                .addFilterAt(new LoginFilter(authenticationManager(authenticationConfiguration),jwtUtil,refreshRepository), UsernamePasswordAuthenticationFilter.class);
//
//        return http.build();
//
//    }
//}
