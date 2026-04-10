package com.lecture.content.service;

import com.lecture.content.domain.ContentType;
import com.lecture.content.domain.EduContent;
import com.lecture.content.dto.ContentRequest;
import com.lecture.content.repository.EduContentRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class ContentService {

    private final EduContentRepository eduContentRepository;
    private final KafkaTemplate<String, Object> kafkaTemplate;

    private static final String TOPIC_CONTENT_EVENTS = "content-events";

    @Transactional
    public void uploadAndIngest(MultipartFile file, String title, String category) {
        // 1. 파일 정보 저장 (S3 URL 등은 더미로 처리)
        String dummyUrl = "http://dummy-storage.local/contents/" + file.getOriginalFilename();
        
        EduContent content = EduContent.builder()
                .title(title)
                .category(category)
                .type(ContentType.PDF)
                .fileUrl(dummyUrl)
                .build();
        
        EduContent savedContent = eduContentRepository.save(content);

        publishContentUpdatedEvent(savedContent);
    }

    @Transactional
    public void registerContent(ContentRequest request) {
        EduContent content = EduContent.builder()
                .title(request.getTitle())
                .type(request.getType())
                .category(request.getCategory())
                .fileUrl(request.getFileUrl())
                .tags(request.getTags())
                .build();
        EduContent savedContent = eduContentRepository.save(content);
        publishContentUpdatedEvent(savedContent);
    }

    @Transactional(readOnly = true)
    public List<ContentRequest> listContents(String category, ContentType type) {
        List<EduContent> contents;

        if (category != null && type != null) {
            contents = eduContentRepository.findByCategoryAndType(category, type);
        } else if (category != null) {
            contents = eduContentRepository.findByCategory(category);
        } else if (type != null) {
            contents = eduContentRepository.findByType(type);
        } else {
            contents = eduContentRepository.findAll();
        }

        return contents.stream()
                .map(content -> ContentRequest.builder()
                        .title(content.getTitle())
                        .type(content.getType())
                        .category(content.getCategory())
                        .fileUrl(content.getFileUrl())
                        .tags(content.getTags())
                        .build())
                .toList();
    }

    @Transactional
    public void updateContent(Long contentId, ContentRequest request) {
        EduContent content = eduContentRepository.findById(contentId)
                .orElseThrow(() -> new IllegalArgumentException("Content not found: " + contentId));

        content.setTitle(request.getTitle());
        content.setType(request.getType());
        content.setCategory(request.getCategory());
        content.setFileUrl(request.getFileUrl());
        content.setTags(request.getTags());

        eduContentRepository.save(content);
    }

    @Transactional
    public void deleteContent(Long contentId) {
        if (!eduContentRepository.existsById(contentId)) {
            throw new IllegalArgumentException("Content not found: " + contentId);
        }
        eduContentRepository.deleteById(contentId);
    }

    private void publishContentUpdatedEvent(EduContent content) {
        Map<String, Object> payload = new HashMap<>();
        payload.put("content_id", String.valueOf(content.getId()));
        payload.put("title", content.getTitle());
        payload.put("file_url", content.getFileUrl());
        payload.put("category", content.getCategory());

        Map<String, Object> event = new HashMap<>();
        event.put("event_type", "Content.Updated");
        event.put("event_id", "content-" + content.getId());
        event.put("timestamp", LocalDateTime.now().toString());
        event.put("source", "content-management-service");
        event.put("payload", payload);

        log.info("Publishing content update event: {}", event);
        kafkaTemplate.send(TOPIC_CONTENT_EVENTS, event);
    }
}
