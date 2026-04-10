package com.lecture.content.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class EmbeddingEvent {
    @JsonProperty("event_type")
    private String eventType; // Embedding.Completed
    @JsonProperty("content_id")
    private String contentId;
    @JsonProperty("vector_db_collection_name")
    private String vectorDbCollectionName;
    private String status; // SUCCESS, FAILED
    @JsonProperty("occurred_at")
    private LocalDateTime occurredAt;
}
