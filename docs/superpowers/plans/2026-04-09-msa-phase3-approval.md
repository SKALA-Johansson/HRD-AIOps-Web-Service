# Phase 3: Feedback & Approval Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Approval Service to handle approvals and feedback for goals and curriculums.

**Architecture:** A dedicated `approval-service` that tracks the approval lifecycle of resources (GOAL, CURRICULUM). It provides endpoints for HR to approve/reject with comments and for users to view history.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, H2 Database (for testing), JPA, Eureka, Gateway.

---

### Task 1: Approval Service Setup

**Files:**
- Create: `approval-service/build.gradle`
- Create: `approval-service/src/main/resources/application.yml`
- Create: `approval-service/src/main/java/com/lecture/approval/ApprovalApplication.java`
- Create: `approval-service/src/main/java/com/lecture/approval/model/Approval.java`
- Create: `approval-service/src/main/java/com/lecture/approval/repository/ApprovalRepository.java`
- Create: `approval-service/src/main/java/com/lecture/approval/controller/ApprovalController.java`
- Modify: `gateway-server/src/main/resources/application.yml`
- Modify: `settings.gradle` (root)

- [ ] **Step 1: Create `approval-service/build.gradle`**
```gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.4.5'
    id 'io.spring.dependency-management' version '1.1.7'
}

group = 'com.lecture'
version = '0.0.1-SNAPSHOT'

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
}

repositories {
    mavenCentral()
}

ext {
    set('springCloudVersion', "2024.0.0")
}

dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'
    runtimeOnly 'com.h2database:h2'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
    }
}
```

- [ ] **Step 2: Create `approval-service/src/main/resources/application.yml`**
```yaml
server:
  port: 9003

spring:
  application:
    name: approval-service
  datasource:
    url: jdbc:h2:mem:testdb;DB_CLOSE_DELAY=-1
    username: sa
    password:
    driver-class-name: org.h2.Driver
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        dialect: org.hibernate.dialect.H2Dialect

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true
```

- [ ] **Step 3: Create `Approval` Entity**
```java
package com.lecture.approval.model;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "approvals")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Approval {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Enumerated(EnumType.STRING)
    private ResourceType resourceType; // GOAL, CURRICULUM

    private Long resourceId;
    
    @Enumerated(EnumType.STRING)
    private ApprovalAction action; // APPROVE, REJECT

    private String comment;
    private Long approverId;
    private LocalDateTime createdAt;

    public enum ResourceType {
        GOAL, CURRICULUM
    }

    public enum ApprovalAction {
        APPROVE, REJECT
    }

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
```

- [ ] **Step 4: Update Gateway Routes**
```yaml
        - id: approval-service
          uri: lb://APPROVAL-SERVICE
          predicates:
            - Path=/api/v1/approvals/**
```

---

### Task 2: Approval API Implementation & Testing

**Files:**
- Create: `approval-service/src/main/java/com/lecture/approval/dto/ApprovalRequest.java`
- Create: `approval-service/src/main/java/com/lecture/approval/dto/ApiResponse.java`
- Create: `approval-service/src/test/java/com/lecture/approval/controller/ApprovalControllerTest.java`

- [ ] **Step 1: Implement `ApprovalController`**
- [ ] **Step 2: Write `MockMvc` tests for 200 OK responses**
- [ ] **Step 3: Update `settings.gradle` and verify build**

---
