package com.lecture.learning.repository;

import com.lecture.learning.model.Progress;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ProgressRepository extends JpaRepository<Progress, String> {
    List<Progress> findAllByUserId(String userId);
    Optional<Progress> findByUserId(String userId);
    Optional<Progress> findByUserIdAndModuleId(String userId, String moduleId);
    boolean existsByUserIdAndModuleId(String userId, String moduleId);
}
