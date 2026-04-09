package com.lecture.approval.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lecture.approval.dto.ApprovalRequest;
import com.lecture.approval.model.Approval;
import com.lecture.approval.repository.ApprovalRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
public class ApprovalControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ApprovalRepository approvalRepository;

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        approvalRepository.deleteAll();
    }

    @Test
    void approveGoal_Success() throws Exception {
        // Given
        Long goalId = 1L;
        ApprovalRequest request = new ApprovalRequest(Approval.Action.APPROVE, "Goal looks good");

        // When & Then
        mockMvc.perform(post("/api/v1/approvals/goals/{goalId}", goalId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.message", is("Goal approval recorded")))
                .andExpect(jsonPath("$.data.resourceType", is("GOAL")))
                .andExpect(jsonPath("$.data.resourceId", is(1)))
                .andExpect(jsonPath("$.data.action", is("APPROVE")))
                .andExpect(jsonPath("$.data.comment", is("Goal looks good")));
    }

    @Test
    void getApprovals_Success() throws Exception {
        // Given
        Long resourceId = 1L;
        Approval.ResourceType resourceType = Approval.ResourceType.GOAL;
        
        Approval approval = Approval.builder()
                .resourceType(resourceType)
                .resourceId(resourceId)
                .action(Approval.Action.APPROVE)
                .comment("Approved")
                .build();
        approvalRepository.save(approval);

        // When & Then
        mockMvc.perform(get("/api/v1/approvals")
                        .param("resourceType", "GOAL")
                        .param("resourceId", "1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].resourceType", is("GOAL")))
                .andExpect(jsonPath("$.data[0].resourceId", is(1)));
    }
}
