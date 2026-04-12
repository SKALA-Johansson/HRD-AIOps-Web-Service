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
import java.util.Optional;
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
                String username = emp.get("username") != null ? String.valueOf(emp.get("username")) : "";
                String name = String.valueOf(emp.getOrDefault("name", ""));
                String department = emp.get("department") != null ? String.valueOf(emp.get("department")) : "";

                GrowthReport report = reportMap.get(userId);
                if (report == null && username != null && !username.isBlank()) {
                    report = reportMap.get(username);
                }
                Integer avgScore = null;
                if (report != null && report.getAchievementMetrics() != null) {
                    avgScore = report.getAchievementMetrics().get("averageScore");
                }

                result.add(UserSummaryDto.builder()
                        .userId(userId)
                        .username(username)
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
        String username = resolveUsernameByUserId(userId);
        Optional<GrowthReport> byUserId = growthReportRepository.findByUserId(userId);
        Optional<GrowthReport> byUsername = (username == null || username.isBlank())
                ? Optional.empty()
                : growthReportRepository.findByUserId(username);

        return byUserId
                .or(() -> byUsername)
                .map(report -> toDto(report, username == null || username.isBlank() ? report.getUserId() : username))
                .orElseGet(() -> GrowthReportDto.builder()
                        .userId(userId)
                        .username(username)
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

    private GrowthReportDto toDto(GrowthReport growthReport, String username) {
        return GrowthReportDto.builder()
                .userId(growthReport.getUserId())
                .username(username)
                .strengths(growthReport.getStrengths())
                .weaknesses(growthReport.getWeaknesses())
                .achievementMetrics(growthReport.getAchievementMetrics())
                .build();
    }

    @SuppressWarnings({"unchecked", "rawtypes"})
    private String resolveUsernameByUserId(String userId) {
        try {
            Map response = restTemplate.getForObject(
                    authServerUrl + "/api/v1/profiles/employees", Map.class);
            if (response == null) {
                return userId;
            }

            Object dataObj = response.get("data");
            if (!(dataObj instanceof List)) {
                return userId;
            }

            List<Map> employees = (List<Map>) dataObj;
            for (Map emp : employees) {
                String candidateUserId = String.valueOf(emp.getOrDefault("userId", ""));
                if (!userId.equals(candidateUserId)) {
                    continue;
                }
                Object usernameObj = emp.get("username");
                if (usernameObj != null) {
                    String username = String.valueOf(usernameObj).trim();
                    if (!username.isBlank()) {
                        return username;
                    }
                }
                break;
            }
        } catch (Exception e) {
            log.warn("username 조회 실패(userId={}): {}", userId, e.getMessage());
        }
        return userId;
    }
}
