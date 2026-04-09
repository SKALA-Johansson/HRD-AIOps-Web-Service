package com.lecture.approval.repository;

import com.lecture.approval.model.Approval;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ApprovalRepository extends JpaRepository<Approval, Long> {
    List<Approval> findByResourceTypeAndResourceId(Approval.ResourceType resourceType, Long resourceId);
}
