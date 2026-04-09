package com.lecture.tutor.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TutorRequest {
    private Long userId;
    private Long curriculumId;
    private String question;
}
