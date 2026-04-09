package com.lecture.report.controller;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(ReportController.class)
class ReportControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("개인 성장 리포트 조회 API 테스트")
    void getUserReportTest() throws Exception {
        Long userId = 1L;

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
