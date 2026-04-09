# Phase 4: Learning Platform Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Learning Platform Service to manage learning content, assignments, and student progress.

**Architecture:** A dedicated `learning-service` that interacts with students. It tracks module content (PDF, Video), manages assignment submissions, and calculates overall progress rates.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, H2 Database (for testing), JPA, Eureka, Gateway.

---

### Task 1: Learning Service Setup

**Files:**
- Create: `learning-service/build.gradle`
- Create: `learning-service/src/main/resources/application.yml`
- Create: `learning-service/src/main/java/com/lecture/learning/LearningApplication.java`
- Create: `learning-service/src/main/java/com/lecture/learning/model/Content.java`
- Create: `learning-service/src/main/java/com/lecture/learning/model/Submission.java`
- Create: `learning-service/src/main/java/com/lecture/learning/model/Progress.java`
- Modify: `gateway-server/src/main/resources/application.yml`
- Modify: `settings.gradle` (root)

- [ ] **Step 1: Create `learning-service/build.gradle`**
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

- [ ] **Step 2: Create `learning-service/src/main/resources/application.yml`**
```yaml
server:
  port: 9004

spring:
  application:
    name: learning-service
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

- [ ] **Step 3: Update Gateway Routes**
```yaml
        - id: learning-service
          uri: lb://LEARNING-SERVICE
          predicates:
            - Path=/api/v1/learning/**
```

---

### Task 2: Learning API Implementation & Testing

**Files:**
- Create: `learning-service/src/main/java/com/lecture/learning/dto/ApiResponse.java`
- Create: `learning-service/src/main/java/com/lecture/learning/dto/SubmissionRequest.java`
- Create: `learning-service/src/main/java/com/lecture/learning/controller/LearningController.java`
- Create: `learning-service/src/test/java/com/lecture/learning/controller/LearningControllerTest.java`

- [ ] **Step 1: Implement `LearningController` with Mock Responses**
    - `GET /api/v1/learning/curriculums/me`
    - `GET /api/v1/learning/modules/{moduleId}/contents`
    - `POST /api/v1/learning/assignments/{assignmentId}/submissions`
    - `GET /api/v1/learning/progress/me`
- [ ] **Step 2: Write `MockMvc` tests to verify API specification**
- [ ] **Step 3: Update `settings.gradle` and run full build**

---
