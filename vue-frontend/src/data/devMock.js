/**
 * 개발 미리보기(isDevPreview) 전용 더미 데이터
 * 백엔드 미연결 시 UI 검증용 — 운영에서는 사용하지 않음
 */

export const MOCK_PROGRESS = {
  completionRate: 62,
  completedModules: 5,
  totalModules: 8
}

export const MOCK_DASHBOARD = {
  totalEmployees: 48,
  avgCompletionRate: 71.4,
  delayedLearners: 4,
  topWeaknessAreas: ['SQL', '네트워크 기초', '운영 배포']
}

export const MOCK_ASSIGNMENT_ID = '501'

export function mockCurriculum(curriculumId) {
  const id = Number(curriculumId) || 301
  return {
    curriculumId: id,
    goalId: 101,
    title: `더미 커리큘럼 #${id} (API 미연결 시 표시)`,
    status: 'APPROVED',
    modules: [
      { moduleId: 1, week: 1, title: 'SKMS · 조직문화' },
      { moduleId: 2, week: 2, title: 'Python · API 실습' },
      { moduleId: 3, week: 3, title: 'LLM 기초' }
    ]
  }
}

export function mockModuleContents(moduleId) {
  const id = String(moduleId)
  const rows = {
    '1': [
      {
        contentId: 1101,
        title: 'SKMS 개요 (더미 자료)',
        type: 'PDF',
        url: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
      },
      { contentId: 1102, title: '온보딩 체크리스트', type: 'LINK', url: '#' }
    ],
    '2': [
      { contentId: 1201, title: 'Python 문법 복습 영상', type: 'VIDEO', url: '#' },
      { contentId: 1202, title: 'REST API 실습 노트', type: 'PDF', url: '#' }
    ],
    '3': [{ contentId: 1301, title: 'LLM 개념 소개', type: 'PDF', url: '#' }]
  }
  return (
    rows[id] || [
      {
        contentId: 1999,
        title: `모듈 ${moduleId} 학습 자료 (더미)`,
        type: 'PDF',
        url: '#'
      }
    ]
  )
}

/**
 * 학습 홈 주차 로드맵 (미리보기·API에 modules 없을 때)
 */
export function sampleWeeklyRoadmap(userName) {
  const who = userName || '신입'
  return [
    {
      week: 1,
      headline: '온보딩 · SKMS',
      items: [
        {
          title: 'SKMS · 조직문화 이해',
          detail: '사내 가치·의사결정 방식',
          moduleId: 1,
          curriculumId: 301,
          status: 'done'
        },
        {
          title: `${who}님 맞춤 온보딩 오리엔테이션`,
          detail: '계열사·직무 소개',
          curriculumId: 301,
          status: 'done'
        }
      ]
    },
    {
      week: 2,
      headline: 'Python · 개발 기초',
      items: [
        {
          title: 'Python 문법·환경 설정',
          detail: '실습 환경 구축',
          moduleId: 2,
          curriculumId: 301,
          status: 'in_progress'
        },
        {
          title: 'REST API 호출 실습',
          detail: '과제: 간단 클라이언트',
          moduleId: 2,
          curriculumId: 303,
          status: 'upcoming'
        }
      ]
    },
    {
      week: 3,
      headline: '데이터 · 협업',
      items: [
        {
          title: 'SQL 기초 & JOIN',
          detail: '사내 DB 가이드라인',
          curriculumId: 302,
          status: 'upcoming'
        },
        {
          title: '코드 리뷰 · Git 워크플로',
          detail: '팀 컨벤션',
          curriculumId: 301,
          status: 'upcoming'
        }
      ]
    },
    {
      week: 4,
      headline: 'AI · LLM 입문',
      items: [
        {
          title: 'LLM 개념 & 프롬프트 설계',
          detail: 'RAG 개요',
          moduleId: 3,
          curriculumId: 304,
          status: 'upcoming'
        },
        {
          title: 'AI 튜터 활용 가이드',
          detail: '질문·과제 피드백',
          curriculumId: 304,
          status: 'upcoming'
        }
      ]
    }
  ]
}

export function sampleCoursesForUser(userName) {
  const who = userName || '신입'
  return [
    {
      curriculumId: 301,
      title: `${who}님을 위한 AI/Data 온보딩 로드맵`,
      status: '진행 중',
      company: 'SKT',
      thumbnailUrl: 'https://picsum.photos/seed/hrd1/400/225'
    },
    {
      curriculumId: 302,
      title: 'SKMS · 조직문화 이해',
      status: '수강 가능',
      company: 'SK HRD',
      thumbnailUrl: 'https://picsum.photos/seed/hrd2/400/225'
    },
    {
      curriculumId: 303,
      title: 'Python · API 실습 미니 프로젝트',
      status: '예정',
      company: 'Learning Platform',
      thumbnailUrl: 'https://picsum.photos/seed/hrd3/400/225'
    },
    {
      curriculumId: 304,
      title: 'LLM · RAG 실무 입문',
      status: 'DRAFT',
      company: 'SK HRD',
      thumbnailUrl: 'https://picsum.photos/seed/hrd4/400/225'
    }
  ]
}

/** HR 승인 대기 — PDF·AI 생성 커리큘럼 큐 (미리보기 전용) */
export const MOCK_PENDING_CURRICULA = [
  {
    curriculumId: 401,
    goalId: 201,
    title: 'PDF: 클라우드·Kubernetes 온보딩 (AI 초안)',
    status: 'PENDING_APPROVAL',
    summary: '6주 · 모듈 9개 · DevOps 기초',
    sourceType: 'PDF_AI',
    createdAt: '2026-04-08T10:30:00',
    modules: [
      { moduleId: 4011, week: 1, title: '컨테이너·Docker 기초' },
      { moduleId: 4012, week: 1, title: '이미지 빌드·레지스트리' },
      { moduleId: 4013, week: 2, title: 'Kubernetes 아키텍처' },
      { moduleId: 4014, week: 2, title: 'Pod·Deployment 실습' },
      { moduleId: 4015, week: 3, title: 'Service·Ingress' },
      { moduleId: 4016, week: 4, title: 'ConfigMap·Secret' },
      { moduleId: 4017, week: 5, title: '관측성·로그' },
      { moduleId: 4018, week: 5, title: '헬스체크·리소스 한도' },
      { moduleId: 4019, week: 6, title: '온콜·장애 대응 입문' }
    ]
  },
  {
    curriculumId: 402,
    goalId: 202,
    title: 'PDF: 데이터 엔지니어링 파이프라인 (AI 초안)',
    status: 'PENDING_APPROVAL',
    summary: '5주 · 모듈 7개 · SQL·배치·품질',
    sourceType: 'PDF_AI',
    createdAt: '2026-04-07T15:00:00',
    modules: [
      { moduleId: 4021, week: 1, title: 'DW·레이어 개념' },
      { moduleId: 4022, week: 2, title: 'SQL 심화·최적화' },
      { moduleId: 4023, week: 2, title: 'Airflow 개요' },
      { moduleId: 4024, week: 3, title: 'DAG 설계 실습' },
      { moduleId: 4025, week: 4, title: '데이터 품질·검증' },
      { moduleId: 4026, week: 5, title: '모니터링·알림' },
      { moduleId: 4027, week: 5, title: '과제: 일배치 파이프라인 설계' }
    ]
  },
  {
    curriculumId: 403,
    goalId: 203,
    title: 'LLM·RAG 사내 교안 기반 로드맵 (AI 초안)',
    status: 'DRAFT',
    summary: '4주 · 모듈 6개 · 프롬프트·RAG',
    sourceType: 'PDF_AI',
    createdAt: '2026-04-06T09:00:00',
    modules: [
      { moduleId: 4031, week: 1, title: 'LLM 동작·한계' },
      { moduleId: 4032, week: 1, title: '프롬프트 엔지니어링' },
      { moduleId: 4033, week: 2, title: '임베딩·벡터 DB' },
      { moduleId: 4034, week: 3, title: 'RAG 파이프라인' },
      { moduleId: 4035, week: 3, title: '할루시네이션 완화' },
      { moduleId: 4036, week: 4, title: '과제: 사내 문서 Q&A PoC' }
    ]
  }
]

export const MOCK_TEAM_PROGRESS = [
  { userId: 1, name: '김신입', completionRate: 62, status: '정상', lastModule: 'Python 실습' },
  { userId: 2, name: '이신입', completionRate: 38, status: '지연', lastModule: 'SKMS' },
  { userId: 3, name: '박신입', completionRate: 88, status: '정상', lastModule: 'LLM 기초' }
]

export const MOCK_TUTOR_GUIDE = {
  weekFocus: '이번 주: SQL JOIN 이해도가 낮음 (리포트 기반 더미)',
  talkingPoints: [
    'INNER vs LEFT 차이를 업무 예시(주문–고객)로 짚어주세요.',
    '서브쿼리 대신 WITH(CTE)로 정리하는 습관을 권장합니다.',
    '다음 면담에서 과제 501 피드백의 "개선점" 항목을 함께 복기하세요.'
  ],
  suggestedQuestions: [
    '실무에서 가장 헷갈렸던 조인 시나리오는 무엇이었나요?',
    '인덱스가 쿼리 플랜에 미치는 영향을 설명해 볼 수 있나요?'
  ]
}
