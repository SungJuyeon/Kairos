package com.project.back.config;
//cors 처리해야 데이터가 제대로 보내짐

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsMvcConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry corsRegistry) {
        corsRegistry.addMapping("/**")
                .allowedOrigins("http://localhost:8081");
    }
}

//컨트롤러단에서 로그인을 구현하려면 현재 등록한 LoginFilter를 등록하지 않으면 POST : /login 경로까지 요청이 넘어온다.

/*
axios나 fetch를 통해 로그인을 진행하신 후 받은 토큰을 로컬 스토리지에 저장하고, 매 요청마다 다시 꺼내어 헤더에 붙여서 보내시면 됩니다.
이때 매요청마다 해당 구문을 적을 필요 없이 axios의 경우 axios interceptor라는 기술을 사용하여
 요청에 대해 동일하게 작업을 수행하는 인터셉터를 구현할 수 있습니다. */