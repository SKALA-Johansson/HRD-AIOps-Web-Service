# Phase 5: AI Tutor Agent Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement AI Tutor Service to handle AI questioning, automated assignment grading, and feedback retrieval.

**Architecture:** A dedicated `tutor-service` that interacts with users for real-time AI assistance. It will later integrate with OpenAI API for LLM capabilities. For now, it provides the API structure and mock responses.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, H2 Database (for testing), JPA, Eureka, Gateway.

---

### Task 1: AI Tutor Service Setup

**Files:**
- Create: `tutor-service/build.gradle`
- Create: `tutor-service/src/main/resources/application.yml`
- Create: `tutor-service/src/main/java/com/lecture/tutor/TutorApplication.java`
- Create: `tutor-service/src/main/java/com/lecture/tutor/model/TutorSession.java`
- Create: `tutor-service/src/main/java/com/lecture/tutor/model/Feedback.java`
- Modify: `gateway-server/src/main/resources/application.yml`
- Modify: `settings.gradle` (root)

- [ ] **Step 1: Create `tutor-service/build.gradle`**
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

- [ ] **Step 2: Create `tutor-service/src/main/resources/application.yml`**
```yaml
server:
  port: 9005

spring:
  application:
    name: tutor-service
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
        - id: tutor-service
          uri: lb://TUTOR-SERVICE
          predicates:
            - Path=/api/v1/tutor/**
```

---

### Task 2: AI Tutor API Implementation & Testing

**Files:**
- Create: `tutor-service/src/main/java/com/lecture/tutor/dto/ApiResponse.java`
- Create: `tutor-service/src/main/java/com/lecture/tutor/dto/TutorRequest.java`
- Create: `tutor-service/src/main/java/com/lecture/tutor/controller/TutorController.java`
- Create: `tutor-service/src/test/java/com/lecture/tutor/controller/TutorControllerTest.java`

- [ ] **Step 1: Implement `TutorController` with Mock Responses**
    - `POST /api/v1/tutor/sessions`: Ask a question to AI.
    - `POST /api/v1/tutor/assignments/{submissionId}/grade`: Request auto-grading.
    - `GET /api/v1/tutor/feedback/{submissionId}`: Get feedback for a submission.
- [ ] **Step 2: Write `MockMvc` tests to verify API specification**
- [ ] **Step 3: Update `settings.gradle` and run full build**

---
