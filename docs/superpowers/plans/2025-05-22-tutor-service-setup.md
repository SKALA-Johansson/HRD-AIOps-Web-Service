# AI Tutor Service Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up the `tutor-service` as a new Spring Cloud microservice with Web, Data JPA, Eureka, H2, and Lombok dependencies.

**Architecture:** A Spring Boot microservice integrated into the existing MSA. It uses H2 for in-memory storage and registers itself with the Eureka server.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, H2 Database, Lombok.

---

### Task 1: Project Configuration

**Files:**
- Create: `tutor-service/build.gradle`
- Modify: `settings.gradle`

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
    // Web
    implementation 'org.springframework.boot:spring-boot-starter-web'

    // JPA + H2
    implementation 'org.springframework.boot:spring-boot-starter-data-jpa'
    runtimeOnly 'com.h2database:h2'

    // Eureka Client
    implementation 'org.springframework.cloud:spring-cloud-starter-netflix-eureka-client'

    // Lombok
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    // Test
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

dependencyManagement {
    imports {
        mavenBom "org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}"
    }
}

tasks.named('test') {
    useJUnitPlatform()
}
```

- [ ] **Step 2: Update `settings.gradle` to include `tutor-service`**

```gradle
rootProject.name = 'web-service-teamproject'
include 'auth-server'
include 'eureka-server'
include 'gateway-server'
include 'goal-setter-service'
include 'curriculum-service'
include 'approval-service'
include 'learning-service'
include 'tutor-service'
```

- [ ] **Step 3: Verify gradle sync (optional but recommended)**

Run: `./gradlew help`
Expected: SUCCESS

---

### Task 2: Service Configuration and Bootstrap

**Files:**
- Create: `tutor-service/src/main/resources/application.yml`
- Create: `tutor-service/src/main/java/com/lecture/tutor/TutorApplication.java`

- [ ] **Step 1: Create `tutor-service/src/main/resources/application.yml`**

```yaml
server:
  port: 9005

spring:
  application:
    name: tutor-service
  datasource:
    url: jdbc:h2:mem:tutordb
    driverClassName: org.h2.Driver
    username: sa
    password:
  h2:
    console:
      enabled: true
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
```

- [ ] **Step 2: Create `tutor-service/src/main/java/com/lecture/tutor/TutorApplication.java`**

```java
package com.lecture.tutor;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
public class TutorApplication {
    public static void main(String[] args) {
        SpringApplication.run(TutorApplication.class, args);
    }
}
```

---

### Task 3: Domain Models

**Files:**
- Create: `tutor-service/src/main/java/com/lecture/tutor/model/TutorSession.java`
- Create: `tutor-service/src/main/java/com/lecture/tutor/model/Feedback.java`

- [ ] **Step 1: Create `TutorSession.java`**

```java
package com.lecture.tutor.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class TutorSession {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Long userId;
    private Long curriculumId;
    @Column(columnDefinition = "TEXT")
    private String question;
    @Column(columnDefinition = "TEXT")
    private String answer;
}
```

- [ ] **Step 2: Create `Feedback.java`**

```java
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
```

---

### Task 4: Gateway Routing

**Files:**
- Modify: `gateway-server/src/main/resources/application.yml`

- [ ] **Step 1: Add route for `tutor-service` in `gateway-server`**

```yaml
        - id: tutor-service
          uri: lb://TUTOR-SERVICE
          predicates:
            - Path=/api/v1/tutor/**
```

---

### Task 5: Final Verification

- [ ] **Step 1: Run build to verify compilation**

Run: `./gradlew :tutor-service:build`
Expected: BUILD SUCCESSFUL
