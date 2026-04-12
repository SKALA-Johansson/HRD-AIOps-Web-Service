package com.lecture.report.dto;

import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserSummaryDto {
    private String userId;
    private String username;
    private String name;
    private String department;
    private Integer completionRate;
    private String status;
    private String lastModule;
}
