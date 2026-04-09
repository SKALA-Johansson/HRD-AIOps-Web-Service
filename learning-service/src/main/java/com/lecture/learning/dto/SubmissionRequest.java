package com.lecture.learning.dto;

import lombok.*;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SubmissionRequest {
    private String answerText;
    private List<String> attachmentUrls;
}
