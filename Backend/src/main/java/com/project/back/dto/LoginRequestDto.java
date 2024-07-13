
package com.project.back.dto;

import jakarta.validation.constraints.NotEmpty;
import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class LoginRequestDto {
    @NotEmpty
    private String loginId;
    @NotEmpty
    private String password;

    private String name;
    private String email;
}
