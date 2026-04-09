package com.lecture.tutor.repository;

import com.lecture.tutor.model.Feedback;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface FeedbackRepository extends JpaRepository<Feedback, Long> {
    Optional<Feedback> findTopBySubmissionIdOrderByIdDesc(Long submissionId);
}
