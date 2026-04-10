package com.lecture.content.domain;

import jakarta.persistence.*;
import lombok.*;

import java.util.List;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EduContent {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String title;

    @Enumerated(EnumType.STRING)
    private ContentType type;

    private String category;

    private String fileUrl;

    private String vectorDbCollectionName; // Added for VDB mapping

    @ElementCollection
    private List<String> tags;
}
