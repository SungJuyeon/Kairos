package com.project.back.dto;

import java.util.Map;

public class MemberUpdate {
    private String email;
    private Map<String, String> fields;

    public String getEmail() {
        return email;
    }
    public void setEmail(String email) {
        this.email = email;
    }
    public Map<String, String> getFields() {
        return fields;
    }
    public void setFields(Map<String, String> fields) {
        this.fields = fields;
    }

}
