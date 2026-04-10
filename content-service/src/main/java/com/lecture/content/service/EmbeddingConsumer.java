package com.lecture.content.service;

import com.lecture.content.domain.EduContent;
import com.lecture.content.repository.EduContentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class EmbeddingConsumer {

    private final EduContentRepository eduContentRepository;

    @KafkaListener(topics = "embedding-events", groupId = "content-group")
    @Transactional
    public void consumeEmbeddingEvent(Map<String, Object> event) {
        log.info("Received embedding completion event: {}", event);

        String eventType = stringValue(event.get("event_type"));
        if (eventType.isBlank()) {
            eventType = stringValue(event.get("eventType")); // backward compatibility
        }
        if (!"Embedding.Completed".equals(eventType)) {
            return;
        }

        Map<String, Object> payload = payload(event.get("payload"), event);
        String contentIdValue = firstNonBlank(
                stringValue(payload.get("content_id")),
                stringValue(payload.get("contentId"))
        );
        if (contentIdValue.isBlank()) {
            return;
        }

        Long contentId = Long.valueOf(contentIdValue);
        EduContent content = eduContentRepository.findById(contentId)
                .orElseThrow(() -> new RuntimeException("Content not found: " + contentId));

        String collectionName = firstNonBlank(
                stringValue(payload.get("vector_db_collection_name")),
                stringValue(payload.get("vectorDbCollectionName"))
        );
        content.setVectorDbCollectionName(collectionName);
        eduContentRepository.save(content);

        log.info("Successfully synced embedding metadata for content ID: {}", contentId);
    }

    private Map<String, Object> payload(Object payloadObj, Map<String, Object> fallback) {
        if (payloadObj instanceof Map<?, ?> map) {
            Map<String, Object> parsed = new HashMap<>();
            map.forEach((k, v) -> parsed.put(String.valueOf(k), v));
            return parsed;
        }
        return fallback;
    }

    private String stringValue(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private String firstNonBlank(String first, String second) {
        return first != null && !first.isBlank() ? first : (second == null ? "" : second);
    }
}
