package com.lecture.auth.controller;

import com.lecture.auth.dto.ApiResponse;
import com.lecture.auth.dto.LoginRequest;
import com.lecture.auth.dto.SignupRequest;
import com.lecture.auth.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;

    @PostMapping("/signup")
    public ResponseEntity<ApiResponse<Object>> signup(@Valid @RequestBody SignupRequest request) {
        Object data = authService.signup(request);
        return ResponseEntity.status(201).body(ApiResponse.success("AUTH-201", "회원가입이 완료되었습니다.", data));
    }

    @PostMapping("/login")
    public ResponseEntity<ApiResponse<Object>> login(@Valid @RequestBody LoginRequest request) {
        Object data = authService.login(request);
        return ResponseEntity.ok(ApiResponse.success("AUTH-200", "로그인에 성공했습니다.", data));
    }
}
