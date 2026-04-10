package com.lecture.learning.service;

import com.lecture.learning.model.Progress;
import com.lecture.learning.repository.ProgressRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class CurriculumApprovedConsumer {

    private final ProgressRepository progressRepository;

    @KafkaListener(topics = "learning-events", groupId = "learning-group")
    @Transactional
    public void consumeApproval(Map<String, Object> event) {
        log.info("Received curriculum approval for learning activation: {}", event);

        String eventType = String.valueOf(event.get("event_type"));
        Object payloadObj = event.get("payload");
        if (!(payloadObj instanceof Map<?, ?> payloadMap)) {
            return;
        }

        if ("Curriculum.Approved".equals(eventType)) {
            String targetId = payloadMap.get("target_id") == null ? "" : String.valueOf(payloadMap.get("target_id"));
            String userId = payloadMap.get("user_id") == null ? "unknown-user" : String.valueOf(payloadMap.get("user_id"));

            // 사원의 학습 진도 레코드 초기화 (기존에 없다면)
            // 실제 운영 환경에서는 Curriculum-Service를 통해 모듈 목록을 가져와 각각 생성해야 함
            // 여기서는 예시로 'targetId'가 가리키는 커리큘럼의 학습 활성화를 의미함
            
            // 임시 moduleId (실제로는 여러 모듈이 생성되어야 함)
            if (targetId.isBlank()) {
                return;
            }
            String dummyModuleId = "mod-" + targetId.substring(0, Math.min(8, targetId.length()));
            
            Progress progress = Progress.builder()
                    .userId(userId)
                    .moduleId(dummyModuleId)
                    .status("NOT_STARTED")
                    .completionRate(0.0)
                    .lastAccessedAt(LocalDateTime.now())
                    .build();

            progressRepository.save(progress);
            log.info("Initialized learning progress for user: {}, module: {}", progress.getUserId(), progress.getModuleId());
        }
    }
}
