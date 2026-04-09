package com.lecture.approval.dto;

import com.lecture.approval.model.Approval;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ApprovalRequest {
    private Approval.Action action;
    private String comment;
}
