package com.lecture.curriculum.service;

import com.lecture.curriculum.dto.CurriculumGenerateRequest;
import com.lecture.curriculum.model.Curriculum;
import com.lecture.curriculum.model.Module;
import com.lecture.curriculum.repository.CurriculumRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class CurriculumService {

    private final CurriculumRepository curriculumRepository;

    @Transactional
    public Map<String, Object> generateCurriculum(CurriculumGenerateRequest request) {
        Curriculum curriculum = Curriculum.builder()
                .goalId(request.getGoalId())
                .title("AI/Data 직무 맞춤형 온보딩 커리큘럼")
                .status(Curriculum.CurriculumStatus.GENERATING)
                .build();

        List<Module> modules = new ArrayList<>();
        modules.add(Module.builder().week(1).title("SKMS 기본 이해").curriculum(curriculum).build());
        modules.add(Module.builder().week(2).title("Python 숙련도 향상").curriculum(curriculum).build());
        curriculum.setModules(modules);

        Curriculum savedCurriculum = curriculumRepository.save(curriculum);

        return Map.of(
                "curriculumId", savedCurriculum.getId(),
                "status", savedCurriculum.getStatus().name()
        );
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getCurriculum(Long curriculumId) {
        Curriculum curriculum = curriculumRepository.findById(curriculumId)
                .orElseGet(() -> {
                    Curriculum fallback = Curriculum.builder()
                            .id(curriculumId)
                            .goalId(101L)
                            .title("AI/Data 직무 맞춤형 온보딩 커리큘럼")
                            .status(Curriculum.CurriculumStatus.DRAFT)
                            .build();
                    List<Module> fallbackModules = new ArrayList<>();
                    fallbackModules.add(Module.builder().id(1L).week(1).title("SKMS 기본 이해").curriculum(fallback).build());
                    fallbackModules.add(Module.builder().id(2L).week(2).title("Python 숙련도 향상").curriculum(fallback).build());
                    fallback.setModules(fallbackModules);
                    return fallback;
                });

        List<Map<String, Object>> modules = curriculum.getModules() == null
                ? List.of()
                : curriculum.getModules().stream()
                        .map(module -> Map.<String, Object>of(
                                "moduleId", module.getId(),
                                "week", module.getWeek(),
                                "title", module.getTitle()
                        ))
                        .toList();

        return Map.of(
                "curriculumId", curriculum.getId(),
                "goalId", curriculum.getGoalId(),
                "title", curriculum.getTitle(),
                "status", curriculum.getStatus().name(),
                "modules", modules
        );
    }
}
