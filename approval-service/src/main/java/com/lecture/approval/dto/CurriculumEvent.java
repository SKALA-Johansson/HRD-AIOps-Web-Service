package com.lecture.approval.dto;

import lombok.*;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CurriculumEvent {
    private String eventType; // e.g., "Goal.Defined"
    private String goalId;
    private String employeeId;
    private String employeeName;
    private String department;
    private String title;
    private String description;
    private List<ModuleItem> modules;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ModuleItem {
        private String title;
        private String description;
        private int week;
    }
}
