package com.lecture.tutor.service;

import com.lecture.tutor.dto.TutorRequest;
import com.lecture.tutor.model.Feedback;
import com.lecture.tutor.model.TutorSession;
import com.lecture.tutor.repository.FeedbackRepository;
import com.lecture.tutor.repository.TutorSessionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class TutorService {

    private final TutorSessionRepository tutorSessionRepository;
    private final FeedbackRepository feedbackRepository;

    @Transactional
    public Map<String, Object> askQuestion(TutorRequest request) {
        TutorSession session = TutorSession.builder()
                .userId(request.getUserId())
                .curriculumId(request.getCurriculumId())
                .question(request.getQuestion())
                .answer("이 커리큘럼은 AI 역량 강화를 목표로 하며, 기본 수학부터 딥러닝 실무까지 다룹니다.")
                .build();

        TutorSession savedSession = tutorSessionRepository.save(session);

        return Map.of(
                "sessionId", savedSession.getId(),
                "answer", savedSession.getAnswer(),
                "references", List.of("Section 1: AI Intro", "Section 2: Python basics")
        );
    }

    @Transactional
    public Map<String, Object> requestGrading(Long submissionId) {
        boolean feedbackExists = feedbackRepository.findTopBySubmissionIdOrderByIdDesc(submissionId).isPresent();

        if (!feedbackExists) {
            Feedback feedback = Feedback.builder()
                    .submissionId(submissionId)
                    .score(87)
                    .strengths(List.of("Excellent explanation of deep learning concepts", "Good code structure"))
                    .improvements(List.of("More detailed error analysis would be helpful", "Try to optimize the learning rate"))
                    .build();
            feedbackRepository.save(feedback);
        }

        return Map.of("gradingStatus", "IN_PROGRESS");
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getFeedback(Long submissionId) {
        Feedback feedback = feedbackRepository.findTopBySubmissionIdOrderByIdDesc(submissionId)
                .orElseGet(() -> Feedback.builder()
                        .submissionId(submissionId)
                        .score(87)
                        .strengths(List.of("Excellent explanation of deep learning concepts", "Good code structure"))
                        .improvements(List.of("More detailed error analysis would be helpful", "Try to optimize the learning rate"))
                        .build());

        return Map.of(
                "score", feedback.getScore(),
                "strengths", feedback.getStrengths(),
                "improvements", feedback.getImprovements()
        );
    }
}
