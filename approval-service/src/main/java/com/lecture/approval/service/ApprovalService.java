package com.lecture.approval.service;

import com.lecture.approval.dto.ApprovalRequest;
import com.lecture.approval.model.Approval;
import com.lecture.approval.repository.ApprovalRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ApprovalService {

    private final ApprovalRepository approvalRepository;

    @Transactional
    public Approval approveGoal(Long goalId, ApprovalRequest request) {
        Approval approval = Approval.builder()
                .resourceType(Approval.ResourceType.GOAL)
                .resourceId(goalId)
                .action(request.getAction())
                .comment(request.getComment())
                .build();

        return approvalRepository.save(approval);
    }

    @Transactional
    public Approval approveCurriculum(Long curriculumId, ApprovalRequest request) {
        Approval approval = Approval.builder()
                .resourceType(Approval.ResourceType.CURRICULUM)
                .resourceId(curriculumId)
                .action(request.getAction())
                .comment(request.getComment())
                .build();

        return approvalRepository.save(approval);
    }

    @Transactional(readOnly = true)
    public List<Approval> getApprovals(Approval.ResourceType resourceType, Long resourceId) {
        return approvalRepository.findByResourceTypeAndResourceId(resourceType, resourceId);
    }
}
