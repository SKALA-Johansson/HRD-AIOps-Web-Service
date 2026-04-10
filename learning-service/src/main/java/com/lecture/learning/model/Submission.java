package com.lecture.learning.model;

import jakarta.persistence.*;
import lombok.*;
import java.util.UUID;

@Entity
@Table(name = "assignments")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Submission {
    @Id
    @Column(name = "assignment_id", length = 36)
    private String submissionId;

    @Column(name = "module_id", length = 36)
    private String assignmentId; // 실제로는 moduleId나 task ID일 수 있음 (init.sql 기준 module_id)

    @Column(name = "user_id", length = 36)
    private String userId;

    @Column(name = "submission_content", columnDefinition = "TEXT")
    private String answerText;

    private String status;

    @PrePersist
    public void prePersist() {
        if (this.submissionId == null) {
            this.submissionId = UUID.randomUUID().toString();
        }
    }
}
