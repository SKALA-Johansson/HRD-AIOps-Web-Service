package com.lecture.content.repository;

import com.lecture.content.domain.ContentType;
import com.lecture.content.domain.EduContent;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EduContentRepository extends JpaRepository<EduContent, Long> {
    List<EduContent> findByCategory(String category);
    List<EduContent> findByType(ContentType type);
    List<EduContent> findByCategoryAndType(String category, ContentType type);
}
