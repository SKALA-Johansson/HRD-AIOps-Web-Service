package com.lecture.content.service;

import com.lecture.content.domain.ContentType;
import com.lecture.content.domain.EduContent;
import com.lecture.content.dto.ContentRequest;
import com.lecture.content.repository.EduContentRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class ContentService {

    private final EduContentRepository eduContentRepository;

    @Transactional
    public void registerContent(ContentRequest request) {
        EduContent content = EduContent.builder()
                .title(request.getTitle())
                .type(request.getType())
                .category(request.getCategory())
                .fileUrl(request.getFileUrl())
                .tags(request.getTags())
                .build();
        eduContentRepository.save(content);
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

        if (contents.isEmpty()) {
            return List.of(ContentRequest.builder()
                    .title("Sample Backend PDF")
                    .type(ContentType.PDF)
                    .category("BACKEND")
                    .fileUrl("http://example.com/file.pdf")
                    .tags(List.of("java", "spring"))
                    .build());
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
}
