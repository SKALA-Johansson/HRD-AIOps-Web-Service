package com.lecture.goal.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class GoalGenerateRequest {
    private Long userId;
    private Long profileId;
}
