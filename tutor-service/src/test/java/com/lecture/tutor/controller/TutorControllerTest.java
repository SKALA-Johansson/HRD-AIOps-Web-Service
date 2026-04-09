package com.lecture.tutor.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lecture.tutor.dto.TutorRequest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TutorController.class)
class TutorControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    @DisplayName("AI에게 질문하기 API 테스트")
    void askQuestionTest() throws Exception {
        TutorRequest request = TutorRequest.builder()
                .userId(1L)
                .curriculumId(101L)
                .question("What is AI?")
                .build();

        mockMvc.perform(post("/api/v1/tutor/sessions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.sessionId").value(9001))
                .andExpect(jsonPath("$.data.answer").exists())
                .andExpect(jsonPath("$.data.references").isArray());
    }

    @Test
    @DisplayName("과제 자동 채점 요청 API 테스트")
    void requestGradingTest() throws Exception {
        Long submissionId = 555L;

        mockMvc.perform(post("/api/v1/tutor/assignments/{submissionId}/grade", submissionId))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.gradingStatus").value("IN_PROGRESS"));
    }

    @Test
    @DisplayName("피드백 조회 API 테스트")
    void getFeedbackTest() throws Exception {
        Long submissionId = 555L;

        mockMvc.perform(get("/api/v1/tutor/feedback/{submissionId}", submissionId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.score").value(87))
                .andExpect(jsonPath("$.data.strengths").isArray())
                .andExpect(jsonPath("$.data.improvements").isArray());
    }
}
