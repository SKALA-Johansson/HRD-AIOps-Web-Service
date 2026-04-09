# Phase 6: Report & Growth Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Report & Growth Service to provide individual growth reports and HR dashboards.

**Architecture:** A dedicated `report-service` that aggregates learning and feedback data to visualize student growth. It provides detailed metrics for individuals and high-level statistics for HR.

**Tech Stack:** Java 21, Spring Boot 3.4.5, Spring Cloud 2024.0.0, H2 Database (for testing), JPA, Eureka, Gateway.

---

### Task 1: Report Service Setup

**Files:**
- Create: `report-service/build.gradle`
- Create: `report-service/src/main/resources/application.yml`
- Create: `report-service/src/main/java/com/lecture/report/ReportApplication.java`
- Create: `report-service/src/main/java/com/lecture/report/model/GrowthReport.java`
- Modify: `gateway-server/src/main/resources/application.yml`
- Modify: `settings.gradle` (root)

- [ ] **Step 1: Create `report-service/build.gradle`**
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

- [ ] **Step 2: Create `report-service/src/main/resources/application.yml`**
```yaml
server:
  port: 9006

spring:
  application:
    name: report-service
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
        - id: report-service
          uri: lb://REPORT-SERVICE
          predicates:
            - Path=/api/v1/reports/**
```

---

### Task 2: Report API Implementation & Testing

**Files:**
- Create: `report-service/src/main/java/com/lecture/report/dto/ApiResponse.java`
- Create: `report-service/src/main/java/com/lecture/report/controller/ReportController.java`
- Create: `report-service/src/test/java/com/lecture/report/controller/ReportControllerTest.java`

- [ ] **Step 1: Implement `ReportController` with Mock Responses**
    - `GET /api/v1/reports/users/{userId}`: Get individual growth report.
    - `GET /api/v1/reports/dashboard`: Get HR dashboard statistics.
- [ ] **Step 2: Write `MockMvc` tests to verify API specification**
- [ ] **Step 3: Update `settings.gradle` and run full build**

---
