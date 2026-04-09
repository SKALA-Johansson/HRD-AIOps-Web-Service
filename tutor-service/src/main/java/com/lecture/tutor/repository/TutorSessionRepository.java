package com.lecture.tutor.repository;

import com.lecture.tutor.model.TutorSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface TutorSessionRepository extends JpaRepository<TutorSession, Long> {
}
