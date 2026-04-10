package com.lecture.content.dto;

import lombok.*;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ContentEvent {
    private String eventType; // e.g., "Content.Updated"
    private String contentId;
    private String title;
    private String fileUrl;
    private String category;
}
