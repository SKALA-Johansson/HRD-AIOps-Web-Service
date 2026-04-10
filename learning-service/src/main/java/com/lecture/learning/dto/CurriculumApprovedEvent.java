package com.lecture.learning.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CurriculumApprovedEvent {
    @JsonProperty("event_type")
    private String eventType; // Curriculum.Approved
    @JsonProperty("target_type")
    private String targetType; // CURRICULUM
    @JsonProperty("target_id")
    private String targetId; // curriculumId
    @JsonProperty("user_id")
    private String userId; // 승인 대상 사원의 userId
    @JsonProperty("occurred_at")
    private LocalDateTime occurredAt;
}
