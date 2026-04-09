package com.lecture.tutor.controller;

import com.lecture.tutor.dto.ApiResponse;
import com.lecture.tutor.dto.TutorRequest;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/tutor")
@RequiredArgsConstructor
public class TutorController {

    @PostMapping("/sessions")
    public ApiResponse<Object> askQuestion(@RequestBody TutorRequest request) {
        // Mock response
        Map<String, Object> data = Map.of(
                "sessionId", 9001,
                "answer", "이 커리큘럼은 AI 역량 강화를 목표로 하며, 기본 수학부터 딥러닝 실무까지 다룹니다.",
                "references", List.of("Section 1: AI Intro", "Section 2: Python basics")
        );
        return ApiResponse.success("TUTOR-200", "AI 답변이 생성되었습니다.", data);
    }

    @PostMapping("/assignments/{submissionId}/grade")
    public ResponseEntity<ApiResponse<Object>> requestGrading(@PathVariable Long submissionId) {
        // Mock response
        Map<String, Object> data = Map.of(
                "gradingStatus", "IN_PROGRESS"
        );
        return ResponseEntity.status(202).body(ApiResponse.success("TUTOR-202", "자동 채점이 시작되었습니다.", data));
    }

    @GetMapping("/feedback/{submissionId}")
    public ApiResponse<Object> getFeedback(@PathVariable Long submissionId) {
        // Mock response
        Map<String, Object> data = Map.of(
                "score", 87,
                "strengths", List.of("Excellent explanation of deep learning concepts", "Good code structure"),
                "improvements", List.of("More detailed error analysis would be helpful", "Try to optimize the learning rate")
        );
        return ApiResponse.success("TUTOR-200", "피드백 조회가 완료되었습니다.", data);
    }
}
