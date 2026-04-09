# Phase 7: Content Management Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Content Management Service to register, update, and manage educational contents.

**Architecture:** A dedicated `content-service` that handles the lifecycle of educational assets. It allows HR/Instructors to upload content metadata and tags, supporting various formats like PDF and VIDEO.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, H2 Database (for testing), JPA, Eureka, Gateway.

---

### Task 1: Content Service Setup

**Files:**
- Create: `content-service/build.gradle`
- Create: `content-service/src/main/resources/application.yml`
- Create: `content-service/src/main/java/com/lecture/content/ContentApplication.java`
- Create: `content-service/src/main/java/com/lecture/content/model/EduContent.java`
- Modify: `gateway-server/src/main/resources/application.yml`
- Modify: `settings.gradle` (root)

- [ ] **Step 1: Create `content-service/build.gradle`**
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

- [ ] **Step 2: Create `content-service/src/main/resources/application.yml`**
```yaml
server:
  port: 9007

spring:
  application:
    name: content-service
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
        - id: content-service
          uri: lb://CONTENT-SERVICE
          predicates:
            - Path=/api/v1/contents/**
```

---

### Task 2: Content API Implementation & Testing

**Files:**
- Create: `content-service/src/main/java/com/lecture/content/dto/ApiResponse.java`
- Create: `content-service/src/main/java/com/lecture/content/dto/ContentRequest.java`
- Create: `content-service/src/main/java/com/lecture/content/controller/ContentController.java`
- Create: `content-service/src/test/java/com/lecture/content/controller/ContentControllerTest.java`

- [ ] **Step 1: Implement `ContentController` with CRUD Mock Responses**
    - `POST /api/v1/contents`: Register new content.
    - `GET /api/v1/contents`: List contents with filters.
    - `PUT /api/v1/contents/{contentId}`: Update content.
    - `DELETE /api/v1/contents/{contentId}`: Delete content.
- [ ] **Step 2: Write `MockMvc` tests to verify API specification**
- [ ] **Step 3: Update `settings.gradle` and run full build**

---
