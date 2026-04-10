package com.lecture.approval.service;

import com.lecture.approval.model.Approval;
import com.lecture.approval.repository.ApprovalRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class CurriculumConsumer {

    private final ApprovalRepository approvalRepository;

    @KafkaListener(topics = "curriculum-events", groupId = "approval-group")
    @Transactional
    public void consumeCurriculumEvent(Map<String, Object> event) {
        log.info("Received curriculum event for approval: {}", event);

        String eventType = String.valueOf(event.get("event_type"));
        Object payloadObj = event.get("payload");
        if (!(payloadObj instanceof Map<?, ?> payloadMap)) {
            return;
        }

        String goalId = payloadMap.get("goal_id") == null ? "" : String.valueOf(payloadMap.get("goal_id"));
        String title = payloadMap.get("title") == null ? "Untitled" : String.valueOf(payloadMap.get("title"));

        // Goal.Defined (DRAFT) 이벤트인 경우 승인 대기 레코드 생성
        if ("Goal.Defined".equals(eventType)) {
            // 이미 존재하는 대기 건이 있는지 확인 (중복 방지)
            if (!goalId.isBlank() && approvalRepository.findByTargetTypeAndTargetId("CURRICULUM", goalId).isEmpty()) {
                Approval approval = Approval.builder()
                        .targetType("CURRICULUM")
                        .targetId(goalId)
                        .status("PENDING")
                        .comments("AI Agent generated draft: " + title)
                        .build();
                
                approvalRepository.save(approval);
                log.info("Created pending approval for curriculum: {}", goalId);
            }
        }
    }
}
