# Content Service Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up the `content-service` microservice, including its project structure, configuration, and integration with the existing MSA architecture.

**Architecture:** A Spring Boot-based microservice part of a Spring Cloud MSA, using Eureka for discovery and H2 for local storage.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, Spring Data JPA, Lombok, H2.

---

### Task 1: Update Root Configuration

**Files:**
- Modify: `settings.gradle`

- [ ] **Step 1: Include `content-service` in `settings.gradle`**

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
include 'report-service'
include 'content-service'
```

---

### Task 2: Create Content Service Build Configuration

**Files:**
- Create: `content-service/build.gradle`

- [ ] **Step 1: Create `content-service/build.gradle` with required dependencies**

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

---

### Task 3: Create Content Service Configuration

**Files:**
- Create: `content-service/src/main/resources/application.yml`

- [ ] **Step 1: Create `content-service/src/main/resources/application.yml`**

```yaml
server:
  port: 9007

spring:
  application:
    name: content-service
  datasource:
    url: jdbc:h2:mem:contentdb
    driver-class-name: org.h2.Driver
    username: sa
    password:
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true
  h2:
    console:
      enabled: true

eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
```

---

### Task 4: Create Main Application Class

**Files:**
- Create: `content-service/src/main/java/com/lecture/content/ContentApplication.java`

- [ ] **Step 1: Create `ContentApplication.java` with `@EnableDiscoveryClient`**

```java
package com.lecture.content;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

@SpringBootApplication
@EnableDiscoveryClient
public class ContentApplication {
    public static void main(String[] args) {
        SpringApplication.run(ContentApplication.class, args);
    }
}
```

---

### Task 5: Create Domain Model

**Files:**
- Create: `content-service/src/main/java/com/lecture/content/domain/ContentType.java`
- Create: `content-service/src/main/java/com/lecture/content/domain/EduContent.java`

- [ ] **Step 1: Create `ContentType.java` enum**

```java
package com.lecture.content.domain;

public enum ContentType {
    PDF, VIDEO
}
```

- [ ] **Step 2: Create `EduContent.java` entity**

```java
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

    @ElementCollection
    private List<String> tags;
}
```

---

### Task 6: Update Gateway Routing

**Files:**
- Modify: `gateway-server/src/main/resources/application.yml`

- [ ] **Step 1: Add `content-service` route to Gateway**

```yaml
        - id: content-service
          uri: lb://CONTENT-SERVICE
          predicates:
            - Path=/api/v1/contents/**
```

---

### Task 7: Verification

- [ ] **Step 1: Run build to verify setup**

Run: `./gradlew :content-service:build`
Expected: BUILD SUCCESSFUL
