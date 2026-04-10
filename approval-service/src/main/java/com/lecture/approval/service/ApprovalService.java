package com.lecture.approval.service;

import com.lecture.approval.dto.ApprovalRequest;
import com.lecture.approval.model.Approval;
import com.lecture.approval.repository.ApprovalRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class ApprovalService {

    private final ApprovalRepository approvalRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String TOPIC_LEARNING_EVENTS = "learning-events";

    @Transactional
    public Approval processApproval(String approvalId, ApprovalRequest request) {
        Approval approval = approvalRepository.findById(approvalId)
                .orElseThrow(() -> new RuntimeException("Approval request not found"));

        approval.setStatus(request.getAction().name());
        approval.setComments(request.getComment());
        approval.setProcessedAt(LocalDateTime.now());
        
        Approval savedApproval = approvalRepository.save(approval);

        // 승인된 경우 Kafka 이벤트 발행
        if (Approval.Action.APPROVE.equals(request.getAction())) {
            Map<String, Object> event = Map.of(
                "eventType", "Curriculum.Approved",
                "targetType", savedApproval.getTargetType(),
                "targetId", savedApproval.getTargetId(),
                "status", "APPROVED",
                "occurredAt", LocalDateTime.now()
            );
            log.info("Publishing curriculum approval event: {}", event);
            kafkaTemplate.send(TOPIC_LEARNING_EVENTS, event);
        }

        return savedApproval;
    }

    @Transactional(readOnly = true)
    public List<Approval> getApprovals(String targetType, String targetId) {
        return approvalRepository.findByTargetTypeAndTargetId(targetType, targetId);
    }
}
