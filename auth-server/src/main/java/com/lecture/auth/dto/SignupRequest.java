package com.lecture.auth.dto;

import com.lecture.auth.model.User;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class SignupRequest {
    private String email;
    private String password;
    private String name;
    private User.Role role;
}
