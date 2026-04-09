package com.lecture.curriculum.controller;

import com.lecture.curriculum.dto.ApiResponse;
import com.lecture.curriculum.dto.CurriculumGenerateRequest;
import com.lecture.curriculum.service.CurriculumService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/curriculums")
@RequiredArgsConstructor
public class CurriculumController {

    private final CurriculumService curriculumService;

    @PostMapping("/generate")
    public ResponseEntity<ApiResponse<Object>> generateCurriculum(@RequestBody CurriculumGenerateRequest request) {
        Map<String, Object> data = curriculumService.generateCurriculum(request);
        return ResponseEntity.status(202).body(ApiResponse.success("CURRICULUM-202", "커리큘럼 생성 요청이 접수되었습니다.", data));
    }

    @GetMapping("/{curriculumId}")
    public ResponseEntity<ApiResponse<Object>> getCurriculum(@PathVariable Long curriculumId) {
        Map<String, Object> data = curriculumService.getCurriculum(curriculumId);
        return ResponseEntity.ok(ApiResponse.success("CURRICULUM-200", "커리큘럼 조회 성공", data));
    }
}
