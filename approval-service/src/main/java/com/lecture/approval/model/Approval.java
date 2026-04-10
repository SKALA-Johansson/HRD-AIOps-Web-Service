package com.lecture.approval.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "approvals")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Approval {

    @Id
    @Column(name = "approval_id", length = 36)
    private String approvalId;

    @Column(name = "target_type", length = 50)
    private String targetType; // GOAL or CURRICULUM

    @Column(name = "target_id", length = 36, nullable = false)
    private String targetId;

    @Column(name = "approver_id", length = 36)
    private String approverId;

    @Column(length = 50, nullable = false)
    private String status; // PENDING, APPROVED, REJECTED

    @Column(columnDefinition = "TEXT")
    private String comments;

    @Column(name = "processed_at")
    private LocalDateTime processedAt;

    @PrePersist
    public void prePersist() {
        if (this.approvalId == null) {
            this.approvalId = UUID.randomUUID().toString();
        }
        if (this.processedAt == null) {
            this.processedAt = LocalDateTime.now();
        }
    }

    public enum Action {
        APPROVE, REJECT
    }

    public enum ResourceType {
        GOAL, CURRICULUM
    }
}
