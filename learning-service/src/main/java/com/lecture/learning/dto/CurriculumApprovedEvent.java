package com.lecture.learning.dto;

import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CurriculumApprovedEvent {
    private String eventType; // Curriculum.Approved
    private String targetType; // CURRICULUM
    private String targetId; // curriculumId
    private String userId; // 승인 대상 사원의 userId
    private LocalDateTime occurredAt;
}
