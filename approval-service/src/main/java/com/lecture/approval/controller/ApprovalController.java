package com.lecture.approval.controller;

import com.lecture.approval.dto.ApiResponse;
import com.lecture.approval.dto.ApprovalRequest;
import com.lecture.approval.model.Approval;
import com.lecture.approval.repository.ApprovalRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/approvals")
@RequiredArgsConstructor
public class ApprovalController {

    private final ApprovalRepository approvalRepository;

    @PostMapping("/goals/{goalId}")
    public ResponseEntity<ApiResponse<Approval>> approveGoal(
            @PathVariable Long goalId,
            @RequestBody ApprovalRequest request) {
        
        Approval approval = Approval.builder()
                .resourceType(Approval.ResourceType.GOAL)
                .resourceId(goalId)
                .action(request.getAction())
                .comment(request.getComment())
                .build();
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Goal approval recorded", approvalRepository.save(approval)));
    }

    @PostMapping("/curriculums/{curriculumId}")
    public ResponseEntity<ApiResponse<Approval>> approveCurriculum(
            @PathVariable Long curriculumId,
            @RequestBody ApprovalRequest request) {
        
        Approval approval = Approval.builder()
                .resourceType(Approval.ResourceType.CURRICULUM)
                .resourceId(curriculumId)
                .action(request.getAction())
                .comment(request.getComment())
                .build();
        
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(ApiResponse.success("Curriculum approval recorded", approvalRepository.save(approval)));
    }

    @GetMapping
    public ResponseEntity<ApiResponse<List<Approval>>> getApprovals(
            @RequestParam Approval.ResourceType resourceType,
            @RequestParam Long resourceId) {
        
        List<Approval> approvals = approvalRepository.findByResourceTypeAndResourceId(resourceType, resourceId);
        return ResponseEntity.ok(ApiResponse.success(approvals));
    }
}
