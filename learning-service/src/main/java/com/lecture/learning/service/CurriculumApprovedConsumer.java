package com.lecture.learning.service;

import com.lecture.learning.model.Progress;
import com.lecture.learning.repository.ProgressRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.time.LocalDateTime;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class CurriculumApprovedConsumer {

    private final ProgressRepository progressRepository;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${external.curriculum-designer-url:http://curriculum-designer-agent:10022}")
    private String curriculumDesignerUrl;

    @KafkaListener(topics = "learning-events", groupId = "learning-group")
    @Transactional
    public void consumeApproval(Map<String, Object> event) {
        log.info("Received curriculum approval for learning activation: {}", event);

        String eventType = String.valueOf(event.get("event_type"));
        Object payloadObj = event.get("payload");
        if (!(payloadObj instanceof Map<?, ?> payloadMap)) {
            return;
        }

        if (!"Curriculum.Approved".equals(eventType)) {
            return;
        }

        String curriculumId = firstNonBlank(
                payloadMap.get("curriculum_id"),
                payloadMap.get("target_id")
        );
        String userId = firstNonBlank(
                payloadMap.get("employee_id"),
                payloadMap.get("user_id")
        );

        if (curriculumId.isBlank() || userId.isBlank()) {
            log.warn("Skip learning activation due to missing fields. curriculumId={}, userId={}", curriculumId, userId);
            return;
        }

        List<String> moduleIds = fetchModuleIds(curriculumId);
        if (moduleIds.isEmpty()) {
            log.warn("No modules found for curriculum {}. Skip progress initialization.", curriculumId);
            return;
        }

        int initialized = 0;
        for (String moduleId : moduleIds) {
            if (moduleId == null || moduleId.isBlank()) {
                continue;
            }
            if (progressRepository.existsByUserIdAndModuleId(userId, moduleId)) {
                continue;
            }
            Progress progress = Progress.builder()
                    .userId(userId)
                    .moduleId(moduleId)
                    .status("NOT_STARTED")
                    .completionRate(0.0)
                    .lastAccessedAt(LocalDateTime.now())
                    .build();
            progressRepository.save(progress);
            initialized++;
        }

        log.info("Initialized learning progress rows: userId={}, curriculumId={}, modules={}", userId, curriculumId, initialized);
    }

    private List<String> fetchModuleIds(String curriculumId) {
        List<String> moduleIds = new ArrayList<>();
        try {
            String endpoint = curriculumDesignerUrl + "/curriculums/" + curriculumId;
            ResponseEntity<Map> response = restTemplate.getForEntity(endpoint, Map.class);
            if (!response.getStatusCode().is2xxSuccessful() || response.getBody() == null) {
                return moduleIds;
            }

            Object dataObj = response.getBody().get("data");
            if (!(dataObj instanceof Map<?, ?> dataMap)) {
                return moduleIds;
            }
            Object modulesObj = dataMap.get("modules");
            if (!(modulesObj instanceof List<?> modules)) {
                return moduleIds;
            }

            for (Object moduleObj : modules) {
                if (moduleObj instanceof Map<?, ?> m && m.get("moduleId") != null) {
                    moduleIds.add(String.valueOf(m.get("moduleId")));
                }
            }
        } catch (Exception e) {
            log.warn("Failed to fetch modules for curriculum {}: {}", curriculumId, e.getMessage());
        }
        return moduleIds;
    }

    private String firstNonBlank(Object... values) {
        for (Object value : values) {
            if (value == null) continue;
            String s = String.valueOf(value).trim();
            if (!s.isBlank()) {
                return s;
            }
        }
        return "";
    }
}
