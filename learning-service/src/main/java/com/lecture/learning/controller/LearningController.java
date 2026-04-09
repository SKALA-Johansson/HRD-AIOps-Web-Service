package com.lecture.learning.controller;

import com.lecture.learning.dto.ApiResponse;
import com.lecture.learning.dto.SubmissionRequest;
import com.lecture.learning.service.LearningService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/learning")
@RequiredArgsConstructor
public class LearningController {

    private final LearningService learningService;

    @GetMapping("/curriculums/me")
    public ApiResponse<Object> getMyCurriculums() {
        List<Map<String, Object>> data = learningService.getMyCurriculums();
        return ApiResponse.success("내 커리큘럼 목록 조회 성공", data);
    }

    @GetMapping("/modules/{moduleId}/contents")
    public ApiResponse<Object> getModuleContents(@PathVariable Long moduleId) {
        List<Map<String, Object>> data = learningService.getModuleContents(moduleId);
        return ApiResponse.success("학습 콘텐츠 조회 성공", data);
    }

    @PostMapping("/assignments/{assignmentId}/submissions")
    public ResponseEntity<ApiResponse<Object>> submitAssignment(
            @PathVariable Long assignmentId,
            @RequestBody SubmissionRequest request) {
        Map<String, Object> data = learningService.submitAssignment(assignmentId, request);
        return ResponseEntity.status(201).body(ApiResponse.success("LEARNING-201", "과제가 제출되었습니다.", data));
    }

    @GetMapping("/progress/me")
    public ApiResponse<Object> getMyProgress() {
        Map<String, Object> data = learningService.getMyProgress();
        return ApiResponse.success("PROGRESS-200", "학습 진도 조회 성공", data);
    }
}
