package com.lecture.goal.controller;

import com.lecture.goal.dto.ApiResponse;
import com.lecture.goal.dto.GoalGenerateRequest;
import com.lecture.goal.model.Goal;
import com.lecture.goal.model.GoalStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/goals")
@RequiredArgsConstructor
public class GoalController {

    @PostMapping("/generate")
    public ResponseEntity<ApiResponse<Object>> generateGoal(@RequestBody GoalGenerateRequest request) {
        // Mock response for Goal Generation Request
        Map<String, Object> data = Map.of(
                "goalDraftId", 101,
                "status", GoalStatus.GENERATING
        );
        return ResponseEntity.status(202).body(ApiResponse.success("GOAL-202", "교육 목표 생성 요청이 접수되었습니다.", data));
    }

    @GetMapping("/{goalId}")
    public ResponseEntity<ApiResponse<Object>> getGoal(@PathVariable Long goalId) {
        // Mock response for Goal Retrieval
        Map<String, Object> data = Map.of(
                "goalId", goalId,
                "userId", 1,
                "title", "SKT AI/Data 직무 신입 역량 강화",
                "description", "LLM 기초, Python 실습, 사내 문화 이해를 포함한 맞춤 목표",
                "status", GoalStatus.DRAFT
        );
        return ResponseEntity.ok(ApiResponse.success("GOAL-200", "교육 목표 조회 성공", data));
    }
}
