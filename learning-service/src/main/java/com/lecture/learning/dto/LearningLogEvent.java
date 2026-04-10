package com.lecture.learning.dto;

import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LearningLogEvent {
    private String eventType; // Learning.ActivityLogged
    private String userId;
    private String moduleId;
    private String activityType; // CONTENT_VIEWED, ASSIGNMENT_SUBMITTED 등
    private Double progressRate;
    private LocalDateTime occurredAt;
}
