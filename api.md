# 스마트 HRD AIOps API 명세서 초안

## 3.1 공통 규칙

### Base URL

```
http://{gateway-host}:8080/api/v1
```

### 공통 헤더

```
Content-Type: application/json
Authorization: Bearer {accessToken}
```

### 공통 응답 형식

```
{
  "success":true,
  "code":"COMMON-200",
  "message":"요청이 성공했습니다.",
  "data": {}
}
```

### 공통 에러 응답

```
{
  "success":false,
  "code":"AUTH-401",
  "message":"인증이 필요합니다.",
  "data":null
}
```

---

## 3.2 Auth / User & Profile Service

### 1) 회원가입

**POST** `/auth/signup`

### Request

```
{
  "name":"홍길동",
  "email":"hong@example.com",
  "password":"Password123!",
  "role":"EMPLOYEE"
}
```

### Response

```
{
  "success":true,
  "code":"AUTH-201",
  "message":"회원가입이 완료되었습니다.",
  "data": {
    "userId":1,
    "email":"hong@example.com",
    "role":"EMPLOYEE"
  }
}
```

---

### 2) 로그인

**POST** `/auth/login`

### Request

```
{
  "email":"hong@example.com",
  "password":"Password123!"
}
```

### Response

```
{
  "success":true,
  "code":"AUTH-200",
  "message":"로그인에 성공했습니다.",
  "data": {
    "accessToken":"jwt-access-token",
    "refreshToken":"jwt-refresh-token",
    "user": {
      "userId":1,
      "name":"홍길동",
      "role":"EMPLOYEE"
    }
  }
}
```

---

### 3) 내 프로필 조회

**GET** `/profiles/me`

### Response

```
{
  "success":true,
  "code":"PROFILE-200",
  "message":"프로필 조회 성공",
  "data": {
    "profileId":10,
    "userId":1,
    "desiredCompany":"SKT",
    "desiredJob":"AI/Data",
    "careerHistory":"컴퓨터공학부 학생",
    "selfIntroduction":"LLM 개발에 관심이 있음",
    "preAssessment": {
      "python":78,
      "sql":61,
      "ml":55
    }
  }
}
```

---

### 4) 프로필 등록/수정

**PUT** `/profiles/me`

### Request

```
{
  "desiredCompany":"SKT",
  "desiredJob":"AI/Data",
  "careerHistory":"캡스톤 프로젝트 수행",
  "selfIntroduction":"LLM 및 백엔드 개발에 관심이 있음",
  "preAssessment": {
    "python":78,
    "sql":61,
    "ml":55
  }
}
```

### Response

```
{
  "success":true,
  "code":"PROFILE-200",
  "message":"프로필이 저장되었습니다.",
  "data": {
    "profileId":10
  }
}
```

---

## 3.3 Goal Setter Agent Service

### 5) 개인 교육 목표 자동 생성 요청

**POST** `/goals/generate`

### Request

```
{
  "userId":1,
  "profileId":10
}
```

### Response

```
{
  "success":true,
  "code":"GOAL-202",
  "message":"교육 목표 생성 요청이 접수되었습니다.",
  "data": {
    "goalDraftId":101,
    "status":"GENERATING"
  }
}
```

---

### 6) 개인 교육 목표 조회

**GET** `/goals/{goalId}`

### Response

```
{
  "success":true,
  "code":"GOAL-200",
  "message":"교육 목표 조회 성공",
  "data": {
    "goalId":101,
    "userId":1,
    "title":"SKT AI/Data 직무 신입 역량 강화",
    "description":"LLM 기초, Python 실습, 사내 문화 이해를 포함한 맞춤 목표",
    "status":"DRAFT"
  }
}
```

---

### 7) HR 교육 목표 수동 정의

**POST** `/goals`

### Request

```
{
  "targetType":"GROUP",
  "company":"SK hynix",
  "jobFamily":"Backend",
  "title":"백엔드 신입 온보딩 목표",
  "description":"Spring Boot, DB, 운영 기초 역량 확보"
}
```

---

## 3.4 Curriculum Designer Agent Service

### 8) 커리큘럼 자동 생성 요청

**POST** `/curriculums/generate`

### Request

```
{
  "goalId":101
}
```

### Response

```
{
  "success":true,
  "code":"CURRICULUM-202",
  "message":"커리큘럼 생성 요청이 접수되었습니다.",
  "data": {
    "curriculumId":301,
    "status":"GENERATING"
  }
}
```

---

### 9) 개인 커리큘럼 조회

**GET** `/curriculums/{curriculumId}`

### Response

```
{
  "success":true,
  "code":"CURRICULUM-200",
  "message":"커리큘럼 조회 성공",
  "data": {
    "curriculumId":301,
    "goalId":101,
    "title":"AI/Data 직무 맞춤형 온보딩 커리큘럼",
    "status":"DRAFT",
    "modules": [
      {
        "moduleId":1,
        "week":1,
        "title":"SKMS 기본 이해"
      },
      {
        "moduleId":2,
        "week":2,
        "title":"Python 숙련도 향상"
      }
    ]
  }
}
```

---

### 10) 커리큘럼 수정 요청

**PUT** `/curriculums/{curriculumId}`

### Request

```
{
  "title":"AI/Data 직무 맞춤형 온보딩 커리큘럼 v2",
  "modules": [
    {
      "moduleId":1,
      "week":1,
      "title":"SKMS 및 조직문화 이해"
    }
  ]
}
```

---

## 3.5 Feedback & Approval Service

### 11) 목표 승인

**POST** `/approvals/goals/{goalId}`

### Request

```
{
  "action":"APPROVE",
  "comment":"적절한 목표입니다."
}
```

---

### 12) 커리큘럼 승인

**POST** `/approvals/curriculums/{curriculumId}`

### Request

```
{
  "action":"APPROVE",
  "comment":"1주차 기본 교육 후 실습 비중 확대 권장"
}
```

---

### 13) 승인 이력 조회

**GET** `/approvals?resourceType=CURRICULUM&resourceId=301`

---

## 3.6 Learning Platform Service

### 14) 내 커리큘럼 목록 조회

**GET** `/learning/curriculums/me`

---

### 15) 학습 콘텐츠 조회

**GET** `/learning/modules/{moduleId}/contents`

### Response

```
{
  "success":true,
  "code":"LEARNING-200",
  "message":"학습 콘텐츠 조회 성공",
  "data": [
    {
      "contentId":1001,
      "title":"SKMS 입문 PDF",
      "type":"PDF",
      "url":"https://example.com/content/1001"
    }
  ]
}
```

---

### 16) 과제 제출

**POST** `/learning/assignments/{assignmentId}/submissions`

### Request

```
{
  "answerText":"과제 답안입니다.",
  "attachmentUrls": [
"https://example.com/files/report.pdf"
  ]
}
```

### Response

```
{
  "success":true,
  "code":"ASSIGNMENT-201",
  "message":"과제가 제출되었습니다.",
  "data": {
    "submissionId":555,
    "status":"SUBMITTED"
  }
}
```

---

### 17) 학습 진도 조회

**GET** `/learning/progress/me`

### Response

```
{
  "success":true,
  "code":"PROGRESS-200",
  "message":"학습 진도 조회 성공",
  "data": {
    "completionRate":62,
    "completedModules":5,
    "totalModules":8
  }
}
```

---

## 3.7 AI Tutor Agent Service

### 18) AI 튜터 질문

**POST** `/tutor/sessions`

### Request

```
{
  "userId":1,
  "curriculumId":301,
  "question":"우리 팀 코딩 컨벤션은 뭐예요?"
}
```

### Response

```
{
  "success":true,
  "code":"TUTOR-200",
  "message":"답변 생성 완료",
  "data": {
    "sessionId":9001,
    "answer":"사내 코딩 컨벤션 문서 기준으로 클래스명은 PascalCase를 사용합니다.",
    "references": [
      {
        "title":"사내 코딩 컨벤션",
        "source":"RAG"
      }
    ]
  }
}
```

---

### 19) 과제 자동 채점 요청

**POST** `/tutor/assignments/{submissionId}/grade`

### Response

```
{
  "success":true,
  "code":"TUTOR-202",
  "message":"자동 채점이 시작되었습니다.",
  "data": {
    "gradingStatus":"IN_PROGRESS"
  }
}
```

---

### 20) 피드백 조회

**GET** `/tutor/feedback/{submissionId}`

### Response

```
{
  "success":true,
  "code":"TUTOR-200",
  "message":"피드백 조회 성공",
  "data": {
    "score":87,
    "strengths": [
"핵심 개념을 정확히 설명함"
    ],
    "improvements": [
"예시 코드 보강 필요"
    ]
  }
}
```

---

## 3.8 Report & Growth Service

### 21) 개인 성장 리포트 조회

**GET** `/reports/users/{userId}`

### Response

```
{
  "success":true,
  "code":"REPORT-200",
  "message":"성장 리포트 조회 성공",
  "data": {
    "reportId":7001,
    "userId":1,
    "strengths": ["Python 문제 해결력"],
    "weaknesses": ["SQL JOIN 이해 부족"],
    "achievementMetrics": {
      "python":85,
      "apiPractice":90
    }
  }
}
```

---

### 22) HR 대시보드 조회

**GET** `/reports/dashboard?company=SKT&jobFamily=AI%2FData`

### Response

```
{
  "success":true,
  "code":"REPORT-200",
  "message":"대시보드 조회 성공",
  "data": {
    "totalEmployees":120,
    "avgCompletionRate":71.4,
    "delayedLearners":9,
    "topWeaknessAreas": ["SQL","네트워크 기초"]
  }
}
```

---

## 3.9 Content Management Service

### 23) 교육 콘텐츠 등록

**POST** `/contents`

### Request

```
{
  "title":"Spring Boot 기초",
  "type":"PDF",
  "category":"BACKEND",
  "fileUrl":"https://example.com/files/spring-basic.pdf",
  "tags": ["spring","backend","java"]
}
```

---

### 24) 콘텐츠 목록 조회

**GET** `/contents?category=BACKEND&type=PDF`

---

### 25) 콘텐츠 수정

**PUT** `/contents/{contentId}`

---

### 26) 콘텐츠 삭제

**DELETE** `/contents/{contentId}`

---

## 3.10 비동기 이벤트 명세

### 1) User.ProfileUpdated

**Topic:** `onboarding-events`

```
{
  "eventType":"User.ProfileUpdated",
  "userId":1,
  "profileId":10,
  "occurredAt":"2026-04-09T10:00:00Z"
}
```

### 2) Goal.Defined

**Topic:** `curriculum-events`

```
{
  "eventType":"Goal.Defined",
  "goalId":101,
  "userId":1,
  "status":"DRAFT",
  "occurredAt":"2026-04-09T10:05:00Z"
}
```

### 3) Curriculum.Approved

**Topic:** `learning-events`

```
{
  "eventType":"Curriculum.Approved",
  "curriculumId":301,
  "userId":1,
  "approvedBy":900,
  "occurredAt":"2026-04-09T10:10:00Z"
}
```

### 4) Learning.ActivityLogged

**Topic:** `learning-logs`

```
{
  "eventType":"Learning.ActivityLogged",
  "userId":1,
  "moduleId":2,
  "activityType":"CONTENT_VIEWED",
  "progressRate":65,
  "occurredAt":"2026-04-09T10:20:00Z"
}
```

### 5) Report.Generated

**Topic:** `reporting-events`

```
{
  "eventType":"Report.Generated",
  "reportId":7001,
  "userId":1,
  "occurredAt":"2026-04-09T10:30:00Z"
}
```