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
public class QuizCompletedConsumer {

    private final ProgressRepository progressRepository;

    @KafkaListener(topics = "learning-logs", groupId = "learning-quiz-group")
    @Transactional
    public void consume(Map<String, Object> event) {
        String eventType = String.valueOf(event.get("event_type"));
        if (!"Learning.QuizCompleted".equals(eventType) && !"Learning.AssignmentCompleted".equals(eventType)) {
            return;
        }

        Object payloadObj = event.get("payload");
        if (!(payloadObj instanceof Map<?, ?> payload)) {
            return;
        }

        String userId = payload.get("user_id") == null ? null : String.valueOf(payload.get("user_id"));
        String moduleId = payload.get("module_id") == null ? null : String.valueOf(payload.get("module_id"));

        if (userId == null || userId.isBlank() || moduleId == null || moduleId.isBlank()
                || "null".equals(userId) || "null".equals(moduleId)) {
            log.debug("[QuizCompleted] user_id or module_id 누락 → 스킵: {}", payload);
            return;
        }

        log.info("[QuizCompleted] Progress 업데이트: userId={}, moduleId={}, eventType={}", userId, moduleId, eventType);

        progressRepository.findByUserIdAndModuleId(userId, moduleId).ifPresentOrElse(
                progress -> {
                    progress.setStatus("COMPLETED");
                    progress.setCompletionRate(100.0);
                    progress.setLastAccessedAt(LocalDateTime.now());
                    progressRepository.save(progress);
                },
                () -> {
                    Progress progress = Progress.builder()
                            .userId(userId)
                            .moduleId(moduleId)
                            .status("COMPLETED")
                            .completionRate(100.0)
                            .lastAccessedAt(LocalDateTime.now())
                            .build();
                    progressRepository.save(progress);
                }
        );
    }
}
