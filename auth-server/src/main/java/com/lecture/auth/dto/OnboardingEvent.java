package com.lecture.auth.dto;

import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OnboardingEvent {
    private String eventType; // e.g., "User.ProfileUpdated"
    private String userId;
    private String username; // Employee ID
    private String name;
    private String department;
    private String pdfUrl;
    private LocalDateTime occurredAt;
}
