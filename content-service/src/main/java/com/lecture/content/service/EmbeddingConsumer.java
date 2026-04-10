package com.lecture.content.service;

import com.lecture.content.domain.EduContent;
import com.lecture.content.dto.EmbeddingEvent;
import com.lecture.content.repository.EduContentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Slf4j
@RequiredArgsConstructor
public class EmbeddingConsumer {

    private final EduContentRepository eduContentRepository;

    @KafkaListener(topics = "embedding-events", groupId = "content-group")
    @Transactional
    public void consumeEmbeddingEvent(EmbeddingEvent event) {
        log.info("Received embedding completion event: {}", event);

        if ("Embedding.Completed".equals(event.getEventType())) {
            Long contentId = Long.valueOf(event.getContentId());
            EduContent content = eduContentRepository.findById(contentId)
                    .orElseThrow(() -> new RuntimeException("Content not found: " + contentId));

            // VDB 컬렉션 정보 업데이트 (RDB 동기화)
            content.setVectorDbCollectionName(event.getVectorDbCollectionName());
            eduContentRepository.save(content);
            
            log.info("Successfully synced embedding metadata for content ID: {}", contentId);
        }
    }
}
