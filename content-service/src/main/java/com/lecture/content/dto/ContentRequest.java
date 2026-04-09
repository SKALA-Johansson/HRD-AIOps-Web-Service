package com.lecture.content.dto;

import com.lecture.content.domain.ContentType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ContentRequest {
    private String title;
    private ContentType type;
    private String category;
    private String fileUrl;
    private List<String> tags;
}
