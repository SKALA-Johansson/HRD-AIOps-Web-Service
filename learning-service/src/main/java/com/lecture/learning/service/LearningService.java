package com.lecture.learning.service;

import com.lecture.learning.dto.SubmissionRequest;
import com.lecture.learning.model.Content;
import com.lecture.learning.model.Progress;
import com.lecture.learning.model.Submission;
import com.lecture.learning.repository.ContentRepository;
import com.lecture.learning.repository.ProgressRepository;
import com.lecture.learning.repository.SubmissionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Service
@Slf4j
@RequiredArgsConstructor
public class LearningService {

    private final ContentRepository contentRepository;
    private final SubmissionRepository submissionRepository;
    private final ProgressRepository progressRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private final RestTemplate restTemplate = new RestTemplate();

    private static final String TOPIC_LEARNING_LOGS = "learning-logs";

    @Value("${external.curriculum-designer-url:http://curriculum-designer-agent:10022}")
    private String curriculumDesignerUrl;

    @Transactional(readOnly = true)
    public List<Map<String, Object>> getMyCurriculums(String userId) {
        if (userId == null || userId.isBlank()) {
            return List.of();
        }

        try {
            String endpoint = curriculumDesignerUrl + "/curriculums/employee/" + userId;
            ResponseEntity<Map> response = restTemplate.getForEntity(endpoint, Map.class);
            if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
                log.warn("Failed to fetch curriculums from curriculum-designer-agent. status={}", response.getStatusCode());
                return fallbackCurriculums();
            }

            Object dataObj = response.getBody().get("data");
            if (!(dataObj instanceof List<?> rows)) {
                return List.of();
            }

            Set<String> visibleStatuses = Set.of("APPROVED", "ACTIVE", "COMPLETED");
            List<Map<String, Object>> result = new ArrayList<>();

            for (Object row : rows) {
                if (!(row instanceof Map<?, ?> c)) {
                    continue;
                }

                String status = c.get("status") == null ? "" : String.valueOf(c.get("status")).toUpperCase();
                if (!visibleStatuses.contains(status)) {
                    continue;
                }

                Object curriculumId = c.get("curriculumId");
                if (curriculumId == null) {
                    curriculumId = c.get("id");
                }
                if (curriculumId == null) {
                    continue;
                }

                String title = c.get("title") == null
                        ? "맞춤형 온보딩 커리큘럼"
                        : String.valueOf(c.get("title"));
                List<Map<String, Object>> modules = new ArrayList<>();

                Object modulesObj = c.get("modules");
                if (modulesObj instanceof List<?> moduleRows) {
                    for (Object moduleRow : moduleRows) {
                        if (!(moduleRow instanceof Map<?, ?> m)) {
                            continue;
                        }
                        String moduleId = m.get("moduleId") == null ? null : String.valueOf(m.get("moduleId"));
                        String moduleStatus = "NOT_STARTED";
                        if (moduleId != null) {
                            moduleStatus = progressRepository.findByUserIdAndModuleId(userId, moduleId)
                                    .map(Progress::getStatus)
                                    .orElse("NOT_STARTED");
                        }
                        Map<String, Object> module = new HashMap<>();
                        module.put("moduleId", moduleId);
                        module.put("week", m.get("week") == null ? 1 : m.get("week"));
                        module.put("title", m.get("title") == null ? "모듈" : String.valueOf(m.get("title")));
                        module.put("status", moduleStatus);
                        modules.add(module);
                    }
                    modules.sort(Comparator.comparingInt(m -> toInt(m.get("week"), 1)));
                }

                Map<String, Object> item = new HashMap<>();
                item.put("curriculumId", curriculumId);
                item.put("title", title);
                item.put("status", status);
                item.put("modules", modules);
                result.add(item);
            }

            return result;
        } catch (Exception e) {
            log.warn("Failed to fetch employee curriculums for userId={}: {}", userId, e.getMessage());
            return fallbackCurriculums();
        }
    }

    @Transactional
    public List<Map<String, Object>> getModuleContents(String userId, String moduleId) {
        publishLearningLogEvent(userId, moduleId, "CONTENT_VIEWED", 10.0);

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

        // 과제 제출 시 해당 모듈 Progress를 COMPLETED로 업데이트
        progressRepository.findByUserIdAndModuleId(userId, moduleId).ifPresentOrElse(
                progress -> {
                    progress.setStatus("COMPLETED");
                    progress.setCompletionRate(100.0);
                    progressRepository.save(progress);
                },
                () -> {
                    Progress progress = Progress.builder()
                            .userId(userId)
                            .moduleId(moduleId)
                            .status("COMPLETED")
                            .completionRate(100.0)
                            .build();
                    progressRepository.save(progress);
                }
        );

        // 과제 제출 활동 로그 발행
        publishLearningLogEvent(userId, moduleId, "ASSIGNMENT_SUBMITTED", 100.0);

        return Map.of(
                "submissionId", savedSubmission.getSubmissionId(),
                "status", savedSubmission.getStatus()
        );
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getMyProgress(String userId) {
        List<Progress> progresses = progressRepository.findAllByUserId(userId);

        if (progresses.isEmpty()) {
            return Map.of("completionRate", 0, "completedModules", 0, "totalModules", 0);
        }

        double totalRate = progresses.stream().mapToDouble(p -> p.getCompletionRate() != null ? p.getCompletionRate() : 0.0).average().orElse(0.0);
        long completedModules = progresses.stream()
                .filter(p -> "COMPLETED".equalsIgnoreCase(p.getStatus()) || (p.getCompletionRate() != null && p.getCompletionRate() >= 100.0))
                .count();
        return Map.of(
                "completionRate", (int)totalRate,
                "completedModules", (int) completedModules,
                "totalModules", progresses.size()
        );
    }

    private int toInt(Object value, int fallback) {
        if (value == null) return fallback;
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (Exception e) {
            return fallback;
        }
    }

    private List<Map<String, Object>> fallbackCurriculums() {
        return List.of(
                Map.of("curriculumId", 301, "title", "AI/Data 직무 맞춤형 온보딩 커리큘럼")
        );
    }

    private void publishLearningLogEvent(String userId, String moduleId, String activityType, Double progressRate) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("user_id", userId);
        payload.put("module_id", moduleId);
        payload.put("activity_type", activityType);
        payload.put("progress_rate", progressRate);

        Map<String, Object> event = new HashMap<>();
        event.put("event_type", "Learning.ActivityLogged");
        event.put("event_id", "learning-" + System.currentTimeMillis());
        event.put("timestamp", LocalDateTime.now().toString());
        event.put("source", "learning-platform-service");
        event.put("payload", payload);

        log.info("Publishing learning activity event: {}", event);
        kafkaTemplate.send(TOPIC_LEARNING_LOGS, event);
    }
}
