package com.lecture.report.dto;

import lombok.*;

import java.util.List;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class DashboardStatsDto {
    private Integer totalEmployees;
    private Double avgCompletionRate;
    private Integer delayedLearners;
    private List<String> topWeaknessAreas;
}
