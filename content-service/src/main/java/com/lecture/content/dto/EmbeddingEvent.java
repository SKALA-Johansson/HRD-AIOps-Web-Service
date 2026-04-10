package com.lecture.content.dto;

import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EmbeddingEvent {
    private String eventType; // Embedding.Completed
    private String contentId;
    private String vectorDbCollectionName;
    private String status; // SUCCESS, FAILED
    private LocalDateTime occurredAt;
}
