"""
표준 커리큘럼 시드 데이터
앱 시작 시 standard_curriculums / standard_modules 테이블이 비어있으면 삽입합니다.
"""
import logging
from sqlalchemy.orm import Session
from app.models.standard_curriculum import StandardCurriculum, StandardModule

logger = logging.getLogger(__name__)

STANDARD_CURRICULA_DATA = [
    {
        "department": "AI / 데이터 부서",
        "role": "Common",
        "career_level": "junior",
        "title": "AI/데이터 부서 표준 온보딩 커리큘럼",
        "description": "AI 및 데이터 직군 신입사원을 위한 6주 필수 역량 과정",
        "total_weeks": 6,
        "modules": [
            {
                "week_number": 1,
                "title": "SKMS 및 온보딩",
                "description": "SK 경영 시스템 이해 및 회사 적응",
                "topics": ["SKMS", "온보딩"],
                "learning_objectives": ["SKMS 핵심 가치 이해", "조직 내 협업 방식 습득", "사내 시스템 활용"],
                "estimated_hours": 8,
            },
            {
                "week_number": 2,
                "title": "데이터 처리 및 분석 심화",
                "description": "Pandas, NumPy 기반 데이터 처리 및 시각화",
                "topics": ["Pandas", "NumPy", "데이터분석", "EDA", "시각화", "matplotlib", "seaborn"],
                "learning_objectives": ["데이터 전처리 능력 확보", "EDA 수행 능력", "시각화 보고서 작성"],
                "estimated_hours": 10,
            },
            {
                "week_number": 3,
                "title": "머신러닝 기초 및 파이프라인",
                "description": "Scikit-learn 기반 ML 모델 학습 및 평가",
                "topics": ["머신러닝", "machine learning", "ML", "Scikit-learn", "sklearn", "분류", "회귀"],
                "learning_objectives": ["ML 모델 선택 및 학습", "과적합 방지 전략", "파이프라인 자동화"],
                "estimated_hours": 10,
            },
            {
                "week_number": 4,
                "title": "딥러닝 및 자연어 처리 기초",
                "description": "PyTorch 기반 딥러닝 모델 구현 및 NLP 입문",
                "topics": ["딥러닝", "deep learning", "PyTorch", "TensorFlow", "Keras", "NLP", "자연어처리", "transformer"],
                "learning_objectives": ["딥러닝 모델 구현", "NLP 파이프라인 이해", "HuggingFace 활용"],
                "estimated_hours": 12,
            },
            {
                "week_number": 5,
                "title": "RAG 시스템 구축 실무",
                "description": "LLM 기반 RAG 파이프라인 설계 및 구현",
                "topics": ["RAG", "LangChain", "벡터DB", "Qdrant", "FAISS", "LLM", "임베딩"],
                "learning_objectives": ["RAG 아키텍처 설계", "벡터 검색 구현", "LLM 연동"],
                "estimated_hours": 12,
            },
            {
                "week_number": 6,
                "title": "AIOps 및 API 서빙",
                "description": "ML 모델 배포 및 운영 자동화",
                "topics": ["FastAPI", "MLflow", "Docker", "MLOps", "AIOps", "API 서빙", "모니터링"],
                "learning_objectives": ["모델 API 서빙 구현", "컨테이너 배포", "운영 모니터링"],
                "estimated_hours": 12,
            },
        ],
    },
    {
        "department": "백엔드 개발 부서",
        "role": "Common",
        "career_level": "junior",
        "title": "백엔드 개발 부서 표준 온보딩 커리큘럼",
        "description": "백엔드 개발 직군 신입사원을 위한 6주 필수 역량 과정",
        "total_weeks": 6,
        "modules": [
            {
                "week_number": 1,
                "title": "SKMS 및 온보딩",
                "description": "SK 경영 시스템 이해 및 회사 적응",
                "topics": ["SKMS", "온보딩"],
                "learning_objectives": ["SKMS 핵심 가치 이해", "조직 내 협업 방식 습득", "사내 시스템 활용"],
                "estimated_hours": 8,
            },
            {
                "week_number": 2,
                "title": "Java 및 객체지향 설계",
                "description": "Java 언어 심화 및 OOP 설계 원칙",
                "topics": ["Java", "OOP", "객체지향", "SOLID", "디자인패턴", "GoF"],
                "learning_objectives": ["OOP 설계 원칙 적용", "디자인 패턴 활용", "클린 코드 작성"],
                "estimated_hours": 10,
            },
            {
                "week_number": 3,
                "title": "Spring Boot 핵심 로직",
                "description": "Spring Boot 기반 RESTful API 개발",
                "topics": ["Spring", "Spring Boot", "REST API", "JPA", "Spring MVC", "IoC", "DI"],
                "learning_objectives": ["Spring Boot 프로젝트 구성", "REST API 설계", "JPA 엔티티 매핑"],
                "estimated_hours": 12,
            },
            {
                "week_number": 4,
                "title": "데이터베이스 및 트랜잭션",
                "description": "RDB 설계 및 트랜잭션 관리",
                "topics": ["SQL", "MySQL", "Oracle", "PostgreSQL", "MariaDB", "트랜잭션", "QueryDSL", "인덱스"],
                "learning_objectives": ["DB 스키마 설계", "쿼리 최적화", "트랜잭션 전략 수립"],
                "estimated_hours": 10,
            },
            {
                "week_number": 5,
                "title": "MSA 기반 비동기 통신",
                "description": "마이크로서비스 아키텍처 및 메시지 큐",
                "topics": ["Kafka", "MSA", "마이크로서비스", "RabbitMQ", "Spring Cloud", "Feign"],
                "learning_objectives": ["MSA 서비스 분리 설계", "Kafka 프로듀서/컨슈머 구현", "서비스 간 통신"],
                "estimated_hours": 12,
            },
            {
                "week_number": 6,
                "title": "테스트 및 인프라 기초",
                "description": "자동화 테스트 작성 및 CI/CD 파이프라인 구성",
                "topics": ["JUnit", "Mockito", "Docker", "CI/CD", "GitHub Actions", "테스트", "TestContainers"],
                "learning_objectives": ["단위/통합 테스트 작성", "CI/CD 파이프라인 구성", "Docker 컨테이너화"],
                "estimated_hours": 10,
            },
        ],
    },
    {
        "department": "프론트엔드 개발 부서",
        "role": "Common",
        "career_level": "junior",
        "title": "프론트엔드 개발 부서 표준 온보딩 커리큘럼",
        "description": "프론트엔드 개발 직군 신입사원을 위한 6주 필수 역량 과정",
        "total_weeks": 6,
        "modules": [
            {
                "week_number": 1,
                "title": "SKMS 및 온보딩",
                "description": "SK 경영 시스템 이해 및 회사 적응",
                "topics": ["SKMS", "온보딩"],
                "learning_objectives": ["SKMS 핵심 가치 이해", "조직 내 협업 방식 습득", "사내 시스템 활용"],
                "estimated_hours": 8,
            },
            {
                "week_number": 2,
                "title": "모던 자바스크립트 및 TS",
                "description": "ES6+ 문법 심화 및 TypeScript 기초",
                "topics": ["JavaScript", "TypeScript", "ES6", "자바스크립트", "async/await", "모듈"],
                "learning_objectives": ["ES6+ 문법 활용", "TypeScript 타입 정의", "비동기 처리 패턴"],
                "estimated_hours": 10,
            },
            {
                "week_number": 3,
                "title": "Vue.js 컴포넌트 설계",
                "description": "Vue 3 Composition API 기반 컴포넌트 개발",
                "topics": ["Vue", "Vue.js", "컴포넌트", "Composition API", "Options API"],
                "learning_objectives": ["Composition API 활용", "재사용 가능한 컴포넌트 설계", "Props/Emit 패턴"],
                "estimated_hours": 12,
            },
            {
                "week_number": 4,
                "title": "전역 상태 관리 및 라우팅",
                "description": "Pinia 상태 관리 및 Vue Router 심화",
                "topics": ["Pinia", "Vuex", "Vue Router", "상태관리", "라우팅", "네비게이션 가드"],
                "learning_objectives": ["전역 상태 설계", "라우터 가드 구현", "인증 플로우 처리"],
                "estimated_hours": 10,
            },
            {
                "week_number": 5,
                "title": "API 연동 및 데이터 핸들링",
                "description": "Axios 기반 RESTful API 연동 및 에러 처리",
                "topics": ["Axios", "API 연동", "REST", "비동기", "인터셉터", "에러 핸들링"],
                "learning_objectives": ["API 클라이언트 설계", "에러 핸들링 전략", "캐싱 전략"],
                "estimated_hours": 10,
            },
            {
                "week_number": 6,
                "title": "렌더링 최적화 및 배포",
                "description": "성능 최적화 기법 및 프로덕션 배포",
                "topics": ["Vite", "Webpack", "lazy loading", "Lighthouse", "Nginx", "배포", "CI/CD"],
                "learning_objectives": ["렌더링 성능 측정", "번들 최적화", "프로덕션 배포 자동화"],
                "estimated_hours": 10,
            },
        ],
    },
    {
        "department": "영업 부서",
        "role": "Common",
        "career_level": "junior",
        "title": "영업 부서 표준 온보딩 커리큘럼",
        "description": "영업 직군 신입사원을 위한 6주 필수 역량 과정",
        "total_weeks": 6,
        "modules": [
            {
                "week_number": 1,
                "title": "SKMS 및 온보딩",
                "description": "SK 경영 시스템 이해 및 회사 적응",
                "topics": ["SKMS", "온보딩"],
                "learning_objectives": ["SKMS 핵심 가치 이해", "조직 내 협업 방식 습득", "사내 시스템 활용"],
                "estimated_hours": 8,
            },
            {
                "week_number": 2,
                "title": "세일즈 파이프라인 기초",
                "description": "B2B/B2C 영업 프로세스 및 파이프라인 관리",
                "topics": ["영업", "세일즈", "파이프라인", "리드", "클로징"],
                "learning_objectives": ["영업 파이프라인 이해", "리드 자격 검증", "클로징 기법 습득"],
                "estimated_hours": 8,
            },
            {
                "week_number": 3,
                "title": "CRM 및 데이터 관리",
                "description": "CRM 시스템 활용 및 고객 데이터 분석",
                "topics": ["CRM", "고객관리", "Salesforce", "데이터관리", "영업 리포트"],
                "learning_objectives": ["CRM 시스템 숙달", "고객 데이터 분석", "영업 성과 리포팅"],
                "estimated_hours": 8,
            },
            {
                "week_number": 4,
                "title": "제안 및 프레젠테이션 스킬",
                "description": "고객 맞춤형 제안서 작성 및 프레젠테이션",
                "topics": ["프레젠테이션", "제안서", "PT", "스토리텔링"],
                "learning_objectives": ["설득력 있는 제안서 작성", "프레젠테이션 스킬 향상", "고객 니즈 분석"],
                "estimated_hours": 8,
            },
            {
                "week_number": 5,
                "title": "시장 분석 및 계약 협상",
                "description": "시장 조사 방법론 및 계약 협상 전략",
                "topics": ["시장분석", "협상", "계약", "SWOT", "경쟁사 분석"],
                "learning_objectives": ["시장 조사 수행 능력", "협상 전략 수립", "계약 리스크 파악"],
                "estimated_hours": 8,
            },
            {
                "week_number": 6,
                "title": "Global Biz English",
                "description": "글로벌 비즈니스 환경에서의 영어 커뮤니케이션",
                "topics": ["영어", "English", "비즈니스영어", "이메일", "미팅"],
                "learning_objectives": ["영어 비즈니스 이메일 작성", "영어 미팅 진행", "영어 프레젠테이션"],
                "estimated_hours": 8,
            },
        ],
    },
]


def seed_standard_curricula(db: Session) -> None:
    """standard_curriculums 테이블이 비어있으면 시드 데이터를 삽입합니다."""
    existing_count = db.query(StandardCurriculum).count()
    if existing_count > 0:
        logger.info(f"[Seeder] 표준 커리큘럼 이미 존재 ({existing_count}건) - 시드 건너뜀")
        return

    for data in STANDARD_CURRICULA_DATA:
        sc = StandardCurriculum(
            department=data["department"],
            role=data["role"],
            career_level=data["career_level"],
            title=data["title"],
            description=data["description"],
            total_weeks=data["total_weeks"],
            is_active=True,
        )
        db.add(sc)
        db.flush()  # sc.id 확보

        for mod_data in data["modules"]:
            sm = StandardModule(
                curriculum_id=sc.id,
                week_number=mod_data["week_number"],
                title=mod_data["title"],
                description=mod_data["description"],
                estimated_hours=mod_data["estimated_hours"],
            )
            sm.set_topics(mod_data["topics"])
            sm.set_learning_objectives(mod_data["learning_objectives"])
            db.add(sm)

    db.commit()
    logger.info(f"[Seeder] 표준 커리큘럼 {len(STANDARD_CURRICULA_DATA)}개 부서 시드 완료")
