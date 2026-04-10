package com.lecture.learning.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "learning_progress")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Progress {

    @Id
    @Column(name = "progress_id", length = 36)
    private String progressId;

    @Column(name = "user_id", length = 36, nullable = false)
    private String userId;

    @Column(name = "module_id", length = 36, nullable = false)
    private String moduleId;

    @Column(length = 50)
    private String status; // NOT_STARTED, IN_PROGRESS, COMPLETED

    @Column(name = "completion_rate")
    private Double completionRate;

    @Column(name = "last_accessed_at")
    private LocalDateTime lastAccessedAt;

    @PrePersist
    public void prePersist() {
        if (this.progressId == null) {
            this.progressId = UUID.randomUUID().toString();
        }
        if (this.status == null) {
            this.status = "NOT_STARTED";
        }
        if (this.completionRate == null) {
            this.completionRate = 0.0;
        }
    }
}
