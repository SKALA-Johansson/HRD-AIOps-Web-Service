package com.lecture.learning.model;

import jakarta.persistence.*;
import lombok.*;
import java.util.UUID;

@Entity
@Table(name = "contents")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Content {
    @Id
    @Column(name = "content_id", length = 36)
    private String contentId;

    @Column(name = "module_id", length = 36)
    private String moduleId;

    private String title;

    @Column(name = "content_type")
    private String contentType; // PDF, VIDEO

    @Column(name = "s3_url")
    private String s3Url;

    @PrePersist
    public void prePersist() {
        if (this.contentId == null) {
            this.contentId = UUID.randomUUID().toString();
        }
    }
}
