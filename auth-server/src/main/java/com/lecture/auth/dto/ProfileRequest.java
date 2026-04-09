package com.lecture.auth.dto;

import lombok.*;

import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProfileRequest {
    private String desiredCompany;
    private String desiredJob;
    private String careerHistory;
    private String selfIntroduction;
    private Map<String, Integer> preAssessment;
}
