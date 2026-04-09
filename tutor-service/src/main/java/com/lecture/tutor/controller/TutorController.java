package com.lecture.tutor.controller;

import com.lecture.tutor.dto.ApiResponse;
import com.lecture.tutor.dto.TutorRequest;
import com.lecture.tutor.service.TutorService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/tutor")
@RequiredArgsConstructor
public class TutorController {

    private final TutorService tutorService;

    @PostMapping("/sessions")
    public ApiResponse<Object> askQuestion(@RequestBody TutorRequest request) {
        Map<String, Object> data = tutorService.askQuestion(request);
        return ApiResponse.success("TUTOR-200", "AI 답변이 생성되었습니다.", data);
    }

    @PostMapping("/assignments/{submissionId}/grade")
    public ResponseEntity<ApiResponse<Object>> requestGrading(@PathVariable Long submissionId) {
        Map<String, Object> data = tutorService.requestGrading(submissionId);
        return ResponseEntity.status(202).body(ApiResponse.success("TUTOR-202", "자동 채점이 시작되었습니다.", data));
    }

    @GetMapping("/feedback/{submissionId}")
    public ApiResponse<Object> getFeedback(@PathVariable Long submissionId) {
        Map<String, Object> data = tutorService.getFeedback(submissionId);
        return ApiResponse.success("TUTOR-200", "피드백 조회가 완료되었습니다.", data);
    }
}
