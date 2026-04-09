package com.lecture.learning.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lecture.learning.dto.SubmissionRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class LearningControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void getMyCurriculums_ShouldReturnCurriculums() throws Exception {
        mockMvc.perform(get("/api/v1/learning/curriculums/me"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data[0].curriculumId").value(301));
    }

    @Test
    void getModuleContents_ShouldReturnContents() throws Exception {
        mockMvc.perform(get("/api/v1/learning/modules/1/contents"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data[0].contentId").value(1001))
                .andExpect(jsonPath("$.data[0].type").value("PDF"));
    }

    @Test
    void submitAssignment_ShouldReturn201() throws Exception {
        SubmissionRequest request = new SubmissionRequest();
        request.setAnswerText("과제 제출합니다.");
        request.setAttachmentUrls(List.of("http://example.com/file.pdf"));

        mockMvc.perform(post("/api/v1/learning/assignments/1/submissions")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("LEARNING-201"))
                .andExpect(jsonPath("$.data.submissionId").value(555));
    }

    @Test
    void getMyProgress_ShouldReturnCompletionRate() throws Exception {
        mockMvc.perform(get("/api/v1/learning/progress/me"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.data.completionRate").value(62));
    }
}
