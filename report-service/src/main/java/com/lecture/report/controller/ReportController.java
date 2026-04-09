package com.lecture.report.controller;

import com.lecture.report.dto.ApiResponse;
import com.lecture.report.dto.DashboardStatsDto;
import com.lecture.report.dto.GrowthReportDto;
import com.lecture.report.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping("/users/{userId}")
    public ApiResponse<GrowthReportDto> getUserReport(@PathVariable("userId") Long userId) {
        return ApiResponse.success(reportService.getUserReport(userId));
    }

    @GetMapping("/dashboard")
    public ApiResponse<DashboardStatsDto> getDashboardStats() {
        return ApiResponse.success(reportService.getDashboardStats());
    }
}
