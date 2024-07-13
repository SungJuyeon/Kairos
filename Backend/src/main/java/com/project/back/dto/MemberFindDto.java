package com.project.back.dto;

import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Data
@Getter
@Setter
public class MemberFindDto {
    private String name;
    private String email;
    
}
