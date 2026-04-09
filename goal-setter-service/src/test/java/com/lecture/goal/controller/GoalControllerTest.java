package com.lecture.goal.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lecture.goal.dto.GoalGenerateRequest;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class GoalControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    public void generateGoal_ShouldReturn202AndGeneratingStatus() throws Exception {
        GoalGenerateRequest request = new GoalGenerateRequest();
        request.setUserId(1L);
        request.setProfileId(10L);

        mockMvc.perform(post("/goals/generate")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("GOAL-202"))
                .andExpect(jsonPath("$.data.status").value("GENERATING"));
    }

    @Test
    public void getGoal_ShouldReturn200AndGoalDetails() throws Exception {
        mockMvc.perform(get("/goals/101")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success").value(true))
                .andExpect(jsonPath("$.code").value("GOAL-200"))
                .andExpect(jsonPath("$.data.goalId").value(101));
    }
}
