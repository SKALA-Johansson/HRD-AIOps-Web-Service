package com.lecture.approval.controller;

import com.lecture.approval.dto.ApiResponse;
import com.lecture.approval.dto.ApprovalRequest;
import com.lecture.approval.model.Approval;
import com.lecture.approval.service.ApprovalService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/approvals")
@RequiredArgsConstructor
public class ApprovalController {

    private final ApprovalService approvalService;

    @PostMapping("/{approvalId}/confirm")
    public ResponseEntity<ApiResponse<Approval>> processApproval(
            @PathVariable String approvalId,
            @RequestBody ApprovalRequest request) {
        Approval approval = approvalService.processApproval(approvalId, request);
        return ResponseEntity.ok(ApiResponse.success("Approval processed successfully", approval));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<Approval>>> getApprovals(
            @RequestParam String targetType,
            @RequestParam String targetId) {
        List<Approval> approvals = approvalService.getApprovals(targetType, targetId);
        return ResponseEntity.ok(ApiResponse.success(approvals));
    }
}
