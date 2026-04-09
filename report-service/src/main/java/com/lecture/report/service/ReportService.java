package com.lecture.report.service;

import com.lecture.report.dto.DashboardStatsDto;
import com.lecture.report.dto.GrowthReportDto;
import com.lecture.report.model.GrowthReport;
import com.lecture.report.repository.GrowthReportRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ReportService {

    private final GrowthReportRepository growthReportRepository;

    @Transactional(readOnly = true)
    public GrowthReportDto getUserReport(Long userId) {
        return growthReportRepository.findByUserId(String.valueOf(userId))
                .map(this::toDto)
                .orElseGet(() -> GrowthReportDto.builder()
                        .userId(userId)
                        .strengths(List.of("Python 문제 해결력"))
                        .weaknesses(List.of("SQL JOIN 이해 부족"))
                        .achievementMetrics(Map.of(
                                "python", 85,
                                "apiPractice", 90
                        ))
                        .build());
    }

    @Transactional(readOnly = true)
    public DashboardStatsDto getDashboardStats() {
        return DashboardStatsDto.builder()
                .totalEmployees(120)
                .avgCompletionRate(71.4)
                .delayedLearners(9)
                .topWeaknessAreas(List.of("SQL", "네트워크 기초"))
                .build();
    }

    private GrowthReportDto toDto(GrowthReport growthReport) {
        return GrowthReportDto.builder()
                .userId(Long.parseLong(growthReport.getUserId()))
                .strengths(growthReport.getStrengths())
                .weaknesses(growthReport.getWeaknesses())
                .achievementMetrics(growthReport.getAchievementMetrics())
                .build();
    }
}
