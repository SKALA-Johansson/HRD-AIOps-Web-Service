package com.lecture.content.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ContentEvent {
    @JsonProperty("event_type")
    private String eventType; // e.g., "Content.Updated"
    @JsonProperty("content_id")
    private String contentId;
    private String title;
    @JsonProperty("file_url")
    private String fileUrl;
    private String category;
}
