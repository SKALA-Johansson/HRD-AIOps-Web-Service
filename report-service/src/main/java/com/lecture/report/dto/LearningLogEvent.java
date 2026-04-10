package com.lecture.report.dto;

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
    private String activityType;
    @JsonProperty("progress_rate")
    private Double progressRate;
    @JsonProperty("occurred_at")
    private LocalDateTime occurredAt;
}
