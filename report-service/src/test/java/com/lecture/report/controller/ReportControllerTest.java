package com.lecture.report.controller;

import com.lecture.report.dto.DashboardStatsDto;
import com.lecture.report.dto.GrowthReportDto;
import com.lecture.report.service.ReportService;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ReportController.class)
class ReportControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ReportService reportService;

    @Test
    @DisplayName("개인 성장 리포트 조회 API 테스트")
    void getUserReportTest() throws Exception {
        Long userId = 1L;
        GrowthReportDto dto = GrowthReportDto.builder()
                .userId(userId)
                .strengths(List.of("Python 문제 해결력"))
                .weaknesses(List.of("SQL JOIN 이해 부족"))
                .achievementMetrics(Map.of("python", 85, "apiPractice", 90))
                .build();
        given(reportService.getUserReport(eq(userId))).willReturn(dto);

        mockMvc.perform(get("/api/v1/reports/users/{userId}", userId)
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.userId").value(1))
                .andExpect(jsonPath("$.data.strengths").isArray())
                .andExpect(jsonPath("$.data.weaknesses").isArray())
                .andExpect(jsonPath("$.data.achievementMetrics").isMap());
    }

    @Test
    @DisplayName("HR 대시보드 조회 API 테스트")
    void getDashboardStatsTest() throws Exception {
        DashboardStatsDto dto = DashboardStatsDto.builder()
                .totalEmployees(120)
                .avgCompletionRate(71.4)
                .delayedLearners(9)
                .topWeaknessAreas(List.of("SQL", "네트워크 기초"))
                .build();
        given(reportService.getDashboardStats()).willReturn(dto);

        mockMvc.perform(get("/api/v1/reports/dashboard")
                        .param("company", "SKT")
                        .param("jobFamily", "AI/Data")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.totalEmployees").value(120))
                .andExpect(jsonPath("$.data.avgCompletionRate").value(71.4))
                .andExpect(jsonPath("$.data.topWeaknessAreas").isArray());
    }
}
