package com.lecture.report.repository;

import com.lecture.report.model.GrowthReport;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface GrowthReportRepository extends JpaRepository<GrowthReport, Long> {
    Optional<GrowthReport> findByUserId(String userId);
}
