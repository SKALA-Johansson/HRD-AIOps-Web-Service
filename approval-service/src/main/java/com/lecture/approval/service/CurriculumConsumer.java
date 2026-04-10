package com.lecture.approval.service;

import com.lecture.approval.dto.CurriculumEvent;
import com.lecture.approval.model.Approval;
import com.lecture.approval.repository.ApprovalRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Slf4j
@RequiredArgsConstructor
public class CurriculumConsumer {

    private final ApprovalRepository approvalRepository;

    @KafkaListener(topics = "curriculum-events", groupId = "approval-group")
    @Transactional
    public void consumeCurriculumEvent(CurriculumEvent event) {
        log.info("Received curriculum event for approval: {}", event);

        // Goal.Defined (DRAFT) 이벤트인 경우 승인 대기 레코드 생성
        if ("Goal.Defined".equals(event.getEventType())) {
            // 이미 존재하는 대기 건이 있는지 확인 (중복 방지)
            if (approvalRepository.findByTargetTypeAndTargetId("CURRICULUM", event.getGoalId()).isEmpty()) {
                Approval approval = Approval.builder()
                        .targetType("CURRICULUM")
                        .targetId(event.getGoalId())
                        .status("PENDING")
                        .comments("AI Agent generated draft: " + event.getTitle())
                        .build();
                
                approvalRepository.save(approval);
                log.info("Created pending approval for curriculum: {}", event.getGoalId());
            }
        }
    }
}
