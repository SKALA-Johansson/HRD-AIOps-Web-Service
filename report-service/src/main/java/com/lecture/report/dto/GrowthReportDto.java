package com.lecture.report.dto;

import lombok.*;

import java.util.List;
import java.util.Map;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GrowthReportDto {
    private String userId;
    private String username;
    private List<String> strengths;
    private List<String> weaknesses;
    private Map<String, Integer> achievementMetrics;
}
