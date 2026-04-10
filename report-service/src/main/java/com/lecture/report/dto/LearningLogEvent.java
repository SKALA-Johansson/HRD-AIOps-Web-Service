package com.lecture.report.dto;

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
    private String activityType;
    private Double progressRate;
    private LocalDateTime occurredAt;
}
