package com.lecture.learning.service;

import com.lecture.learning.dto.CurriculumApprovedEvent;
import com.lecture.learning.model.Progress;
import com.lecture.learning.repository.ProgressRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@Slf4j
@RequiredArgsConstructor
public class CurriculumApprovedConsumer {

    private final ProgressRepository progressRepository;

    @KafkaListener(topics = "learning-events", groupId = "learning-group")
    @Transactional
    public void consumeApproval(CurriculumApprovedEvent event) {
        log.info("Received curriculum approval for learning activation: {}", event);

        if ("Curriculum.Approved".equals(event.getEventType())) {
            // 사원의 학습 진도 레코드 초기화 (기존에 없다면)
            // 실제 운영 환경에서는 Curriculum-Service를 통해 모듈 목록을 가져와 각각 생성해야 함
            // 여기서는 예시로 'targetId'가 가리키는 커리큘럼의 학습 활성화를 의미함
            
            // 임시 moduleId (실제로는 여러 모듈이 생성되어야 함)
            String dummyModuleId = "mod-" + event.getTargetId().substring(0, 8);
            
            Progress progress = Progress.builder()
                    .userId(event.getUserId() != null ? event.getUserId() : "unknown-user")
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
