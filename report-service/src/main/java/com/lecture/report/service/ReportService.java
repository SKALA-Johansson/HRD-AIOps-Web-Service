package com.lecture.report.service;

import com.lecture.report.dto.DashboardStatsDto;
import com.lecture.report.dto.GrowthReportDto;
import com.lecture.report.dto.UserSummaryDto;
import com.lecture.report.model.GrowthReport;
import com.lecture.report.repository.GrowthReportRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ReportService {

    private final GrowthReportRepository growthReportRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${external.auth-server-url:http://auth-server:9000}")
    private String authServerUrl;

    @SuppressWarnings({"unchecked", "rawtypes"})
    public List<UserSummaryDto> getUsers() {
        try {
            Map response = restTemplate.getForObject(
                    authServerUrl + "/api/v1/profiles/employees", Map.class);
            if (response == null) return Collections.emptyList();

            Object dataObj = response.get("data");
            if (!(dataObj instanceof List)) return Collections.emptyList();

            List<Map> employees = (List<Map>) dataObj;

            Map<String, GrowthReport> reportMap = growthReportRepository.findAll().stream()
                    .collect(Collectors.toMap(GrowthReport::getUserId, r -> r));

            List<UserSummaryDto> result = new ArrayList<>();
            for (Map emp : employees) {
                String userId = String.valueOf(emp.get("userId"));
                String name = String.valueOf(emp.getOrDefault("name", ""));
                String department = emp.get("department") != null ? String.valueOf(emp.get("department")) : "";

                GrowthReport report = reportMap.get(userId);
                Integer avgScore = null;
                if (report != null && report.getAchievementMetrics() != null) {
                    avgScore = report.getAchievementMetrics().get("averageScore");
                }

                result.add(UserSummaryDto.builder()
                        .userId(userId)
                        .name(name)
                        .department(department)
                        .completionRate(avgScore)
                        .status(report != null ? "IN_PROGRESS" : "NOT_STARTED")
                        .build());
            }
            return result;
        } catch (Exception e) {
            log.error("auth-server 직원 목록 조회 실패: {}", e.getMessage());
            return Collections.emptyList();
        }
    }

    @Transactional(readOnly = true)
    public GrowthReportDto getUserReport(String userId) {
        return growthReportRepository.findByUserId(userId)
                .map(this::toDto)
                .orElseGet(() -> GrowthReportDto.builder()
                        .userId(userId)
                        .strengths(List.of())
                        .weaknesses(List.of())
                        .achievementMetrics(Map.of())
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
                .userId(growthReport.getUserId())
                .strengths(growthReport.getStrengths())
                .weaknesses(growthReport.getWeaknesses())
                .achievementMetrics(growthReport.getAchievementMetrics())
                .build();
    }
}
