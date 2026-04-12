package com.lecture.auth.controller;

import com.lecture.auth.dto.ApiResponse;
import com.lecture.auth.dto.ProfileRequest;
import com.lecture.auth.model.User;
import com.lecture.auth.repository.ProfileRepository;
import com.lecture.auth.repository.UserRepository;
import com.lecture.auth.service.ProfileService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/v1/profiles")
@Slf4j
@RequiredArgsConstructor
public class ProfileController {

    private final ProfileService profileService;
    private final UserRepository userRepository;
    private final ProfileRepository profileRepository;

    @GetMapping("/employees")
    public ResponseEntity<ApiResponse<Object>> getEmployees() {
        List<User> employees = userRepository.findByRole(User.Role.EMPLOYEE);
        List<Map<String, Object>> result = employees.stream().map(u -> {
            Map<String, Object> m = new java.util.HashMap<>();
            m.put("userId", u.getUserId());
            m.put("name", u.getName());
            m.put("username", u.getUsername());
            profileRepository.findByUserUserId(u.getUserId()).ifPresent(p -> {
                m.put("department", p.getDepartment());
            });
            return m;
        }).collect(Collectors.toList());
        return ResponseEntity.ok(ApiResponse.success("PROFILE-200", "직원 목록 조회 성공", result));
    }

    @PostMapping(value = "/register", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<ApiResponse<Object>> registerEmployee(
            @RequestParam("name") String name,
            @RequestParam("username") String username, // Employee ID
            @RequestParam("department") String department,
            @RequestParam("birthDate") String birthDate, // YYMMDD
            @RequestParam("file") MultipartFile file) {

        log.info("Registering new employee: {} ({}) in department: {}", name, username, department);
        Object data = profileService.registerEmployee(name, username, department, birthDate, file);
        return ResponseEntity.ok(ApiResponse.success("PROFILE-201", "사원 등록 및 분석 요청이 완료되었습니다.", data));
    }

    @GetMapping("/me")
    public ResponseEntity<ApiResponse<Object>> getMyProfile(Authentication authentication) {
        String username = authentication.getName();
        Object data = profileService.getProfileByUsername(username);
        return ResponseEntity.ok(ApiResponse.success("PROFILE-200", "프로필 조회 성공", data));
    }

    @PutMapping("/me")
    public ResponseEntity<ApiResponse<Object>> updateMyProfile(Authentication authentication, @Valid @RequestBody ProfileRequest request) {
        String username = authentication.getName();
        Object data = profileService.updateProfileByUsername(username, request);
        return ResponseEntity.ok(ApiResponse.success("PROFILE-200", "프로필이 저장되었습니다.", data));
    }
}
