package com.lecture.goal.service;

import com.lecture.goal.dto.GoalGenerateRequest;
import com.lecture.goal.model.Goal;
import com.lecture.goal.model.GoalStatus;
import com.lecture.goal.repository.GoalRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class GoalService {

    private final GoalRepository goalRepository;

    @Transactional
    public Map<String, Object> generateGoal(GoalGenerateRequest request) {
        Goal goal = Goal.builder()
                .userId(request.getUserId())
                .profileId(request.getProfileId())
                .title("생성 중인 교육 목표")
                .description("프로필 기반 목표 생성이 진행 중입니다.")
                .status(GoalStatus.GENERATING)
                .build();

        Goal savedGoal = goalRepository.save(goal);

        return Map.of(
                "goalDraftId", savedGoal.getId(),
                "status", savedGoal.getStatus()
        );
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getGoal(Long goalId) {
        Goal goal = goalRepository.findById(goalId)
                .orElseGet(() -> Goal.builder()
                        .id(goalId)
                        .userId(1L)
                        .profileId(10L)
                        .title("SKT AI/Data 직무 신입 역량 강화")
                        .description("LLM 기초, Python 실습, 사내 문화 이해를 포함한 맞춤 목표")
                        .status(GoalStatus.DRAFT)
                        .build());

        return Map.of(
                "goalId", goal.getId(),
                "userId", goal.getUserId(),
                "title", goal.getTitle(),
                "description", goal.getDescription(),
                "status", goal.getStatus()
        );
    }
}
