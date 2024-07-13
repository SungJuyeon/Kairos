package com.project.back.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class MemberResponseDto {
    private String sessionId;
    private String message;
    private User user;

    @Getter
    @Setter
    public static class User{
        private String loginId;
        private String name;

        public String getLoginId() {
            return loginId;
        }
        public String getName() {
            return name;
        }

        public void setLoginId(String loginId) {
            this.loginId = loginId;
        }
        public void setName(String name) {
            this.name = name;
        }
    }
}
