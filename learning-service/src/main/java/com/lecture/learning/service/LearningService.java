package com.lecture.learning.service;

import com.lecture.learning.dto.LearningLogEvent;
import com.lecture.learning.dto.SubmissionRequest;
import com.lecture.learning.model.Content;
import com.lecture.learning.model.Progress;
import com.lecture.learning.model.Submission;
import com.lecture.learning.repository.ContentRepository;
import com.lecture.learning.repository.ProgressRepository;
import com.lecture.learning.repository.SubmissionRepository;
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
public class LearningService {

    private final ContentRepository contentRepository;
    private final SubmissionRepository submissionRepository;
    private final ProgressRepository progressRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String TOPIC_LEARNING_LOGS = "learning-logs";

    @Transactional(readOnly = true)
    public List<Map<String, Object>> getMyCurriculums() {
        return List.of(
                Map.of("curriculumId", "cur-ai-001", "title", "AI/Data 직무 맞춤형 온보딩 커리큘럼")
        );
    }

    @Transactional
    public List<Map<String, Object>> getModuleContents(String userId, String moduleId) {
        // 콘텐츠 조회 활동 로그 발행
        LearningLogEvent event = LearningLogEvent.builder()
                .eventType("Learning.ActivityLogged")
                .userId(userId)
                .moduleId(moduleId)
                .activityType("CONTENT_VIEWED")
                .progressRate(10.0)
                .occurredAt(LocalDateTime.now())
                .build();
        
        log.info("Publishing learning activity event: {}", event);
        kafkaTemplate.send(TOPIC_LEARNING_LOGS, event);

        List<Content> contents = contentRepository.findByModuleId(moduleId);
        return contents.stream()
                .map(content -> {
                    Map<String, Object> map = new java.util.HashMap<>();
                    map.put("contentId", content.getContentId());
                    map.put("title", content.getTitle());
                    map.put("type", content.getContentType());
                    map.put("url", content.getS3Url());
                    return map;
                })
                .collect(java.util.stream.Collectors.toList());
    }

    @Transactional
    public Map<String, Object> submitAssignment(String userId, String moduleId, String assignmentId, SubmissionRequest request) {
        Submission submission = Submission.builder()
                .assignmentId(assignmentId)
                .userId(userId)
                .answerText(request.getAnswerText())
                .status("SUBMITTED")
                .build();

        Submission savedSubmission = submissionRepository.save(submission);

        // 과제 제출 활동 로그 발행
        LearningLogEvent event = LearningLogEvent.builder()
                .eventType("Learning.ActivityLogged")
                .userId(userId)
                .moduleId(moduleId)
                .activityType("ASSIGNMENT_SUBMITTED")
                .progressRate(100.0)
                .occurredAt(LocalDateTime.now())
                .build();
        
        log.info("Publishing assignment submission event: {}", event);
        kafkaTemplate.send(TOPIC_LEARNING_LOGS, event);

        return Map.of(
                "submissionId", savedSubmission.getSubmissionId(),
                "status", savedSubmission.getStatus()
        );
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getMyProgress(String userId) {
        List<Progress> progresses = progressRepository.findByUserId(userId).stream().toList();
        
        if (progresses.isEmpty()) {
            return Map.of("completionRate", 0, "totalModules", 0);
        }

        double totalRate = progresses.stream().mapToDouble(p -> p.getCompletionRate() != null ? p.getCompletionRate() : 0.0).average().orElse(0.0);
        return Map.of(
                "completionRate", (int)totalRate,
                "totalModules", progresses.size()
        );
    }
}
