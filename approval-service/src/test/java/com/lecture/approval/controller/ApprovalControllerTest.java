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

import java.util.UUID;

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
    void processApproval_Success() throws Exception {
        // Given
        String approvalId = UUID.randomUUID().toString();
        Approval approval = Approval.builder()
                .approvalId(approvalId)
                .targetType("CURRICULUM")
                .targetId("cur-123")
                .status("PENDING")
                .build();
        approvalRepository.save(approval);

        ApprovalRequest request = new ApprovalRequest(Approval.Action.APPROVE, "Looks good");

        // When & Then
        mockMvc.perform(post("/api/v1/approvals/{approvalId}/confirm", approvalId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.message", is("Approval processed successfully")))
                .andExpect(jsonPath("$.data.status", is("APPROVE")))
                .andExpect(jsonPath("$.data.comments", is("Looks good")));
    }

    @Test
    void getApprovals_Success() throws Exception {
        // Given
        String targetId = "target-123";
        String targetType = "GOAL";
        
        Approval approval = Approval.builder()
                .targetType(targetType)
                .targetId(targetId)
                .status("APPROVED")
                .comments("Approved")
                .build();
        approvalRepository.save(approval);

        // When & Then
        mockMvc.perform(get("/api/v1/approvals")
                        .param("targetType", targetType)
                        .param("targetId", targetId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.success", is(true)))
                .andExpect(jsonPath("$.data", hasSize(1)))
                .andExpect(jsonPath("$.data[0].targetType", is(targetType)))
                .andExpect(jsonPath("$.data[0].targetId", is(targetId)));
    }
}
