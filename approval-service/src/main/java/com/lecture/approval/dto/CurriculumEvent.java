package com.lecture.approval.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CurriculumEvent {
    @JsonProperty("event_type")
    private String eventType; // e.g., "Goal.Defined"
    @JsonProperty("goal_id")
    private String goalId;
    @JsonProperty("employee_id")
    private String employeeId;
    @JsonProperty("employee_name")
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
