package com.lecture.learning.controller;

import com.lecture.learning.dto.ApiResponse;
import com.lecture.learning.dto.SubmissionRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/learning")
@RequiredArgsConstructor
public class LearningController {

    @GetMapping("/curriculums/me")
    public ApiResponse<Object> getMyCurriculums() {
        // Mock response
        List<Map<String, Object>> data = List.of(
                Map.of("curriculumId", 301, "title", "AI/Data 직무 맞춤형 온보딩 커리큘럼")
        );
        return ApiResponse.success("내 커리큘럼 목록 조회 성공", data);
    }

    @GetMapping("/modules/{moduleId}/contents")
    public ApiResponse<Object> getModuleContents(@PathVariable Long moduleId) {
        // Mock response
        List<Map<String, Object>> data = List.of(
                Map.of(
                        "contentId", 1001,
                        "title", "SKMS 입문 PDF",
                        "type", "PDF",
                        "url", "https://example.com/content/1001"
                )
        );
        return ApiResponse.success("학습 콘텐츠 조회 성공", data);
    }

    @PostMapping("/assignments/{assignmentId}/submissions")
    public ResponseEntity<ApiResponse<Object>> submitAssignment(
            @PathVariable Long assignmentId,
            @RequestBody SubmissionRequest request) {
        // Mock response
        Map<String, Object> data = Map.of(
                "submissionId", 555,
                "status", "SUBMITTED"
        );
        return ResponseEntity.status(201).body(ApiResponse.success("LEARNING-201", "과제가 제출되었습니다.", data));
    }

    @GetMapping("/progress/me")
    public ApiResponse<Object> getMyProgress() {
        // Mock response
        Map<String, Object> data = Map.of(
                "completionRate", 62,
                "completedModules", 5,
                "totalModules", 8
        );
        return ApiResponse.success("PROGRESS-200", "학습 진도 조회 성공", data);
    }
}
