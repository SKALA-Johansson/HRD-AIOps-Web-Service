package com.lecture.curriculum.controller;

import com.lecture.curriculum.dto.ApiResponse;
import com.lecture.curriculum.dto.CurriculumGenerateRequest;
import com.lecture.curriculum.model.Curriculum;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/curriculums")
@RequiredArgsConstructor
public class CurriculumController {

    @PostMapping("/generate")
    public ResponseEntity<ApiResponse<Object>> generateCurriculum(@RequestBody CurriculumGenerateRequest request) {
        // Mock response for Curriculum Generation Request
        Map<String, Object> data = Map.of(
                "curriculumId", 301,
                "status", "GENERATING"
        );
        return ResponseEntity.status(202).body(ApiResponse.success("CURRICULUM-202", "커리큘럼 생성 요청이 접수되었습니다.", data));
    }

    @GetMapping("/{curriculumId}")
    public ResponseEntity<ApiResponse<Object>> getCurriculum(@PathVariable Long curriculumId) {
        // Mock response for Curriculum Retrieval
        Map<String, Object> data = Map.of(
                "curriculumId", curriculumId,
                "goalId", 101,
                "title", "AI/Data 직무 맞춤형 온보딩 커리큘럼",
                "status", "DRAFT",
                "modules", List.of(
                        Map.of("moduleId", 1, "week", 1, "title", "SKMS 기본 이해"),
                        Map.of("moduleId", 2, "week", 2, "title", "Python 숙련도 향상")
                )
        );
        return ResponseEntity.ok(ApiResponse.success("CURRICULUM-200", "커리큘럼 조회 성공", data));
    }
}
