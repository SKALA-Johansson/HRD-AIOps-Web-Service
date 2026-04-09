# Phase 2: Agentic AI Services (Goal & Curriculum) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Goal Setter Service and Curriculum Designer Service with basic API, DB, and Eureka/Gateway integration.

**Architecture:** Two new microservices following the same Spring Cloud pattern. `goal-setter-service` handles user educational goals, and `curriculum-designer-service` handles specific curriculum modules. These services will later integrate with OpenAI API.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, MariaDB, JPA, Eureka, Gateway.

---

### Task 1: Goal Setter Service Setup

**Files:**
- Create: `goal-setter-service/build.gradle`
- Create: `goal-setter-service/src/main/resources/application.yml`
- Create: `goal-setter-service/src/main/java/com/lecture/goal/GoalSetterApplication.java`
- Create: `goal-setter-service/src/main/java/com/lecture/goal/model/Goal.java`
- Create: `goal-setter-service/src/main/java/com/lecture/goal/repository/GoalRepository.java`
- Create: `goal-setter-service/src/main/java/com/lecture/goal/controller/GoalController.java`
- Modify: `gateway-server/src/main/resources/application.yml`
- Modify: `settings.gradle` (root)

- [ ] **Step 1: Create `goal-setter-service/build.gradle`**
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
    runtimeOnly 'org.mariadb.jdbc:mariadb-java-client'
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
    }
}
```

- [ ] **Step 2: Create `goal-setter-service/src/main/resources/application.yml`**
```yaml
server:
  port: 9001

spring:
  application:
    name: goal-setter-service
  datasource:
    url: jdbc:mariadb://lecturedb:3306/goal_db
    username: manager
    password: SqlDba-1
    driver-class-name: org.mariadb.jdbc.Driver
  jpa:
    hibernate:
      ddl-auto: update
    properties:
      hibernate:
        dialect: org.hibernate.dialect.MariaDBDialect

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true
```

- [ ] **Step 3: Create `Goal` Entity**
```java
package com.lecture.goal.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "goals")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Goal {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private Long userId;
    private Long profileId;
    private String title;
    private String description;

    @Enumerated(EnumType.STRING)
    private GoalStatus status;

    public enum GoalStatus {
        GENERATING, DRAFT, APPROVED, COMPLETED
    }
}
```

- [ ] **Step 4: Update Gateway Routes**
Modify `gateway-server/src/main/resources/application.yml` to include:
```yaml
        - id: goal-service
          uri: lb://GOAL-SETTER-SERVICE
          predicates:
            - Path=/api/v1/goals/**
```

---

### Task 2: Curriculum Designer Service Setup

**Files:**
- Create: `curriculum-service/build.gradle`
- Create: `curriculum-service/src/main/resources/application.yml`
- Create: `curriculum-service/src/main/java/com/lecture/curriculum/CurriculumApplication.java`
- Create: `curriculum-service/src/main/java/com/lecture/curriculum/model/Curriculum.java`
- Create: `curriculum-service/src/main/java/com/lecture/curriculum/model/Module.java`
- Create: `curriculum-service/src/main/java/com/lecture/curriculum/controller/CurriculumController.java`
- Modify: `gateway-server/src/main/resources/application.yml`
- Modify: `settings.gradle` (root)

- [ ] **Step 1: Setup project and routing (similar to Task 1)**
- [ ] **Step 2: Create `Curriculum` and `Module` Entities**
- [ ] **Step 3: Implement `POST /curriculums/generate` mock response**

---
