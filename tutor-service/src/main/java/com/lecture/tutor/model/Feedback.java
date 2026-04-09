package com.lecture.tutor.model;

import jakarta.persistence.*;
import lombok.*;
import java.util.List;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Feedback {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long submissionId;
    private Integer score;

    @ElementCollection
    private List<String> strengths;

    @ElementCollection
    private List<String> improvements;
}
