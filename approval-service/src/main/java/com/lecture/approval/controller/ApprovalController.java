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

    @PostMapping("/goals/{goalId}")
    public ResponseEntity<ApiResponse<Approval>> approveGoal(
            @PathVariable Long goalId,
            @RequestBody ApprovalRequest request) {
        Approval approval = approvalService.approveGoal(goalId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Goal approval recorded", approval));
    }

    @PostMapping("/curriculums/{curriculumId}")
    public ResponseEntity<ApiResponse<Approval>> approveCurriculum(
            @PathVariable Long curriculumId,
            @RequestBody ApprovalRequest request) {
        Approval approval = approvalService.approveCurriculum(curriculumId, request);
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Curriculum approval recorded", approval));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<Approval>>> getApprovals(
            @RequestParam Approval.ResourceType resourceType,
            @RequestParam Long resourceId) {
        List<Approval> approvals = approvalService.getApprovals(resourceType, resourceId);
        return ResponseEntity.ok(ApiResponse.success(approvals));
    }
}
