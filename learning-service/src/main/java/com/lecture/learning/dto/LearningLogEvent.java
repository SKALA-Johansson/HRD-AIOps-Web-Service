package com.lecture.learning.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LearningLogEvent {
    @JsonProperty("event_type")
    private String eventType; // Learning.ActivityLogged
    @JsonProperty("user_id")
    private String userId;
    @JsonProperty("module_id")
    private String moduleId;
    @JsonProperty("activity_type")
    private String activityType; // CONTENT_VIEWED, ASSIGNMENT_SUBMITTED 등
    @JsonProperty("progress_rate")
    private Double progressRate;
    @JsonProperty("occurred_at")
    private LocalDateTime occurredAt;
}
