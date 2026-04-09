package com.lecture.goal.controller;

import com.lecture.goal.dto.ApiResponse;
import com.lecture.goal.dto.GoalGenerateRequest;
import com.lecture.goal.service.GoalService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/goals")
@RequiredArgsConstructor
public class GoalController {

    private final GoalService goalService;

    @PostMapping("/generate")
    public ResponseEntity<ApiResponse<Object>> generateGoal(@RequestBody GoalGenerateRequest request) {
        Map<String, Object> data = goalService.generateGoal(request);
        return ResponseEntity.status(202).body(ApiResponse.success("GOAL-202", "교육 목표 생성 요청이 접수되었습니다.", data));
    }

    @GetMapping("/{goalId}")
    public ResponseEntity<ApiResponse<Object>> getGoal(@PathVariable Long goalId) {
        Map<String, Object> data = goalService.getGoal(goalId);
        return ResponseEntity.ok(ApiResponse.success("GOAL-200", "교육 목표 조회 성공", data));
    }
}
