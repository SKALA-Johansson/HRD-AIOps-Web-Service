package com.lecture.auth.model;

import jakarta.persistence.*;
import lombok.*;

import java.util.Map;

@Entity
@Table(name = "profiles")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Profile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    private String desiredCompany;
    private String desiredJob;
    private String careerHistory;
    @Column(columnDefinition = "TEXT")
    private String selfIntroduction;

    @ElementCollection
    @CollectionTable(name = "profile_pre_assessments", joinColumns = @JoinColumn(name = "profile_id"))
    @MapKeyColumn(name = "assessment_key")
    @Column(name = "assessment_value")
    private Map<String, Integer> preAssessment;
}
