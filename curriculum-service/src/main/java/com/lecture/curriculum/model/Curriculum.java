package com.lecture.curriculum.model;

import jakarta.persistence.*;
import lombok.*;
import java.util.List;

@Entity
@Table(name = "curriculums")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Curriculum {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long goalId;
    private String title;

    @Enumerated(EnumType.STRING)
    private CurriculumStatus status;

    @OneToMany(mappedBy = "curriculum", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Module> modules;

    public enum CurriculumStatus {
        GENERATING, DRAFT, APPROVED, COMPLETED
    }
}
