package com.lecture.auth.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OnboardingEvent {
    @JsonProperty("event_type")
    private String eventType; // e.g., "User.ProfileUpdated"
    @JsonProperty("user_id")
    private String userId;
    private String username; // Employee ID
    @JsonProperty("employee_name")
    private String name;
    private String department;
    @JsonProperty("pdf_url")
    private String pdfUrl;
    @JsonProperty("occurred_at")
    private LocalDateTime occurredAt;
}
