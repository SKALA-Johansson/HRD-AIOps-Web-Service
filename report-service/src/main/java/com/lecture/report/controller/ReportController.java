package com.lecture.report.controller;

import com.lecture.report.dto.ApiResponse;
import com.lecture.report.dto.DashboardStatsDto;
import com.lecture.report.dto.GrowthReportDto;
import com.lecture.report.dto.UserSummaryDto;
import com.lecture.report.service.ReportService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/reports")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @GetMapping("/users")
    public ApiResponse<List<UserSummaryDto>> getUsers(@RequestParam(required = false) String status) {
        return ApiResponse.success(reportService.getUsers());
    }

    @GetMapping("/users/{userId}")
    public ApiResponse<GrowthReportDto> getUserReport(@PathVariable("userId") String userId) {
        return ApiResponse.success(reportService.getUserReport(userId));
    }

    @GetMapping("/dashboard")
    public ApiResponse<DashboardStatsDto> getDashboardStats() {
        return ApiResponse.success(reportService.getDashboardStats());
    }
}
