package com.lecture.auth.controller;

import com.lecture.auth.dto.ApiResponse;
import com.lecture.auth.dto.ProfileRequest;
import com.lecture.auth.service.ProfileService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/profiles")
@RequiredArgsConstructor
public class ProfileController {

    private final ProfileService profileService;

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<Object>> getMyProfile(Authentication authentication) {
        String email = authentication.getName();
        Object data = profileService.getProfileByEmail(email);
        return ResponseEntity.ok(ApiResponse.success("PROFILE-200", "프로필 조회 성공", data));
    }

    @PutMapping("/me")
    public ResponseEntity<ApiResponse<Object>> updateMyProfile(Authentication authentication, @Valid @RequestBody ProfileRequest request) {
        String email = authentication.getName();
        Object data = profileService.updateProfileByEmail(email, request);
        return ResponseEntity.ok(ApiResponse.success("PROFILE-200", "프로필이 저장되었습니다.", data));
    }
}
