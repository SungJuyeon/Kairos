package com.project.back.dto;

public class AuthenticationResponse {

    private String sessionId;

    public AuthenticationResponse(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
}
