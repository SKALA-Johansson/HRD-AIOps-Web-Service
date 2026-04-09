package com.lecture.report.controller;

import com.lecture.report.dto.ApiResponse;
import com.lecture.report.dto.DashboardStatsDto;
import com.lecture.report.dto.GrowthReportDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/reports")
public class ReportController {

    @GetMapping("/users/{userId}")
    public ApiResponse<GrowthReportDto> getUserReport(@PathVariable("userId") Long userId) {
        GrowthReportDto mockReport = GrowthReportDto.builder()
                .userId(userId)
                .strengths(List.of("Python 문제 해결력"))
                .weaknesses(List.of("SQL JOIN 이해 부족"))
                .achievementMetrics(Map.of(
                        "python", 85,
                        "apiPractice", 90
                ))
                .build();
        return ApiResponse.success(mockReport);
    }

    @GetMapping("/dashboard")
    public ApiResponse<DashboardStatsDto> getDashboardStats() {
        DashboardStatsDto mockStats = DashboardStatsDto.builder()
                .totalEmployees(120)
                .avgCompletionRate(71.4)
                .delayedLearners(9)
                .topWeaknessAreas(List.of("SQL", "네트워크 기초"))
                .build();
        return ApiResponse.success(mockStats);
    }
}
