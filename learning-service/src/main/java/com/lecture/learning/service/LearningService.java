package com.lecture.learning.service;

import com.lecture.learning.dto.SubmissionRequest;
import com.lecture.learning.model.Content;
import com.lecture.learning.model.Progress;
import com.lecture.learning.model.Submission;
import com.lecture.learning.repository.ContentRepository;
import com.lecture.learning.repository.ProgressRepository;
import com.lecture.learning.repository.SubmissionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class LearningService {

    private static final long DEFAULT_USER_ID = 1L;

    private final ContentRepository contentRepository;
    private final SubmissionRepository submissionRepository;
    private final ProgressRepository progressRepository;

    @Transactional(readOnly = true)
    public List<Map<String, Object>> getMyCurriculums() {
        return List.of(
                Map.of("curriculumId", 301L, "title", "AI/Data 직무 맞춤형 온보딩 커리큘럼")
        );
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> getModuleContents(Long moduleId) {
        List<Content> contents = contentRepository.findByModuleId(moduleId);

        if (contents.isEmpty()) {
            return List.of(
                    Map.of(
                            "contentId", 1001L,
                            "title", "SKMS 입문 PDF",
                            "type", "PDF",
                            "url", "https://example.com/content/1001"
                    )
            );
        }

        return contents.stream()
                .map(content -> Map.<String, Object>of(
                        "contentId", content.getId(),
                        "title", content.getTitle(),
                        "type", content.getType(),
                        "url", content.getUrl()
                ))
                .toList();
    }

    @Transactional
    public Map<String, Object> submitAssignment(Long assignmentId, SubmissionRequest request) {
        Submission submission = Submission.builder()
                .assignmentId(assignmentId)
                .userId(DEFAULT_USER_ID)
                .answerText(request.getAnswerText())
                .status("SUBMITTED")
                .build();

        Submission savedSubmission = submissionRepository.save(submission);

        return Map.of(
                "submissionId", savedSubmission.getId(),
                "status", savedSubmission.getStatus()
        );
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getMyProgress() {
        Progress progress = progressRepository.findByUserId(DEFAULT_USER_ID)
                .orElseGet(() -> Progress.builder()
                        .userId(DEFAULT_USER_ID)
                        .completionRate(62.0)
                        .completedModules(5)
                        .build());

        int completionRate = progress.getCompletionRate() == null ? 0 : progress.getCompletionRate().intValue();
        int completedModules = progress.getCompletedModules() == null ? 0 : progress.getCompletedModules();
        int totalModules = Math.max(completedModules, 8);

        return Map.of(
                "completionRate", completionRate,
                "completedModules", completedModules,
                "totalModules", totalModules
        );
    }
}
