"""
부서별 정석 커리큘럼 초기 데이터 투입 스크립트

사용법:
  python seed_standard_curriculums.py           # 전체 시드
  python seed_standard_curriculums.py ai        # AI팀만
  python seed_standard_curriculums.py sales     # 영업팀만

전제:
  - docker-compose up으로 curriculum-designer-agent(:10022)가 기동된 상태
"""
import sys
import requests

BASE = "http://localhost:10022"
URL = f"{BASE}/curriculums/standard"

STANDARD_CURRICULUMS = [
    # ─────────────────────────────────────────────────────────────────
    # 개발팀 / 백엔드 엔지니어 / junior
    # ─────────────────────────────────────────────────────────────────
    {
        "department": "개발팀",
        "role": "백엔드 엔지니어",
        "career_level": "junior",
        "title": "백엔드 엔지니어 신입 정석 커리큘럼",
        "description": "신입 백엔드 엔지니어가 실무 투입 전 반드시 숙지해야 할 12주 기초 과정",
        "total_weeks": 12,
        "modules": [
            {
                "week_number": 1,
                "title": "Java/Python 기초 & OOP 개념",
                "description": "객체지향 프로그래밍 핵심 원칙 이해",
                "topics": ["Java", "Python", "OOP", "클래스", "상속", "다형성", "캡슐화"],
                "learning_objectives": [
                    "SOLID 원칙 설명 가능",
                    "클래스 설계 및 구현",
                    "인터페이스와 추상 클래스 차이 이해",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 2,
                "title": "자료구조 & 알고리즘",
                "description": "실무에서 자주 쓰이는 자료구조와 알고리즘",
                "topics": ["자료구조", "알고리즘", "배열", "링크드리스트", "트리", "해시맵", "정렬", "Big-O"],
                "learning_objectives": [
                    "각 자료구조의 시간/공간 복잡도 이해",
                    "문제 유형별 적합한 자료구조 선택",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 3,
                "title": "관계형 DB & SQL",
                "description": "데이터베이스 설계와 SQL 쿼리 최적화",
                "topics": ["SQL", "MySQL", "MariaDB", "정규화", "인덱스", "JOIN", "트랜잭션", "ACID"],
                "learning_objectives": [
                    "ERD 설계 및 정규화(3NF)",
                    "복잡한 JOIN 쿼리 작성",
                    "인덱스 설계 및 쿼리 최적화",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 4,
                "title": "Spring Boot 기초",
                "description": "Spring Boot 프레임워크로 REST API 개발",
                "topics": ["Spring Boot", "REST API", "JPA", "Hibernate", "Controller", "Service", "Repository"],
                "learning_objectives": [
                    "Spring Boot 프로젝트 구성 이해",
                    "RESTful API 설계 및 구현",
                    "JPA/Hibernate로 DB 연동",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 5,
                "title": "Spring Security & 인증/인가",
                "description": "JWT 기반 인증/인가 구현",
                "topics": ["Spring Security", "JWT", "OAuth2", "인증", "인가", "RBAC"],
                "learning_objectives": [
                    "JWT 토큰 발급 및 검증 구현",
                    "Spring Security 필터 체인 이해",
                    "역할 기반 접근 제어(RBAC) 설계",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 6,
                "title": "Docker & 컨테이너 기초",
                "description": "Docker를 활용한 컨테이너화 및 로컬 개발 환경 구성",
                "topics": ["Docker", "Dockerfile", "Docker Compose", "컨테이너", "이미지"],
                "learning_objectives": [
                    "Dockerfile 작성 및 이미지 빌드",
                    "Docker Compose로 멀티 서비스 구성",
                    "컨테이너 디버깅 방법",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 7,
                "title": "MSA & Spring Cloud 기초",
                "description": "마이크로서비스 아키텍처 개념과 Spring Cloud 생태계",
                "topics": ["MSA", "Spring Cloud", "Eureka", "API Gateway", "서비스 디스커버리", "로드 밸런싱"],
                "learning_objectives": [
                    "MSA와 모놀리스 트레이드오프 이해",
                    "Eureka 서비스 등록/발견 구현",
                    "Spring Cloud Gateway 라우팅 설정",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 8,
                "title": "Apache Kafka 메시징",
                "description": "이벤트 기반 아키텍처와 Kafka 활용",
                "topics": ["Kafka", "메시지큐", "이벤트 드리븐", "토픽", "파티션", "컨슈머 그룹", "오프셋"],
                "learning_objectives": [
                    "Kafka 토픽/파티션 설계",
                    "Producer/Consumer 구현",
                    "이벤트 드리븐 서비스 간 통신 구현",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 9,
                "title": "테스트 전략 & TDD",
                "description": "단위/통합 테스트 작성과 TDD 실습",
                "topics": ["TDD", "JUnit", "Mockito", "단위테스트", "통합테스트", "테스트 커버리지"],
                "learning_objectives": [
                    "JUnit5로 단위 테스트 작성",
                    "Mockito로 의존성 목킹",
                    "TDD 사이클(Red-Green-Refactor) 실습",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 10,
                "title": "CI/CD & GitHub Actions",
                "description": "자동화 빌드/배포 파이프라인 구성",
                "topics": ["CI/CD", "GitHub Actions", "빌드 자동화", "배포", "파이프라인"],
                "learning_objectives": [
                    "GitHub Actions 워크플로우 작성",
                    "테스트 자동화 및 빌드 파이프라인 구성",
                    "Docker 이미지 자동 빌드/푸시",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 11,
                "title": "모니터링 & 로깅",
                "description": "Prometheus, Grafana, ELK로 시스템 관찰성 확보",
                "topics": ["Prometheus", "Grafana", "ELK", "Elasticsearch", "Logstash", "Kibana", "모니터링", "로깅"],
                "learning_objectives": [
                    "Prometheus 메트릭 수집 설정",
                    "Grafana 대시보드 구성",
                    "구조화 로그 작성 및 Kibana 시각화",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 12,
                "title": "팀 프로젝트 실습",
                "description": "실무 프로젝트 협업 실습 및 코드 리뷰",
                "topics": ["코드 리뷰", "Git Flow", "협업", "Pull Request", "리팩토링", "문서화"],
                "learning_objectives": [
                    "Git Flow 브랜치 전략 적용",
                    "코드 리뷰 문화 이해 및 참여",
                    "기술 문서 작성",
                ],
                "estimated_hours": 16,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────────────
    # 데이터팀 / 데이터 엔지니어 / junior
    # ─────────────────────────────────────────────────────────────────
    {
        "department": "데이터팀",
        "role": "데이터 엔지니어",
        "career_level": "junior",
        "title": "데이터 엔지니어 신입 정석 커리큘럼",
        "description": "신입 데이터 엔지니어를 위한 데이터 파이프라인 및 플랫폼 12주 기초 과정",
        "total_weeks": 12,
        "modules": [
            {
                "week_number": 1,
                "title": "Python 데이터 처리 기초",
                "description": "pandas, numpy를 활용한 데이터 처리",
                "topics": ["Python", "pandas", "numpy", "데이터 처리", "EDA"],
                "learning_objectives": [
                    "pandas DataFrame 조작 능숙",
                    "데이터 전처리 파이프라인 구성",
                    "기초 통계 분석",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 2,
                "title": "SQL & 데이터 웨어하우스",
                "description": "고급 SQL과 DW 설계 원칙",
                "topics": ["SQL", "데이터 웨어하우스", "OLAP", "스타 스키마", "파티셔닝", "윈도우 함수"],
                "learning_objectives": [
                    "윈도우 함수 활용 분석 쿼리 작성",
                    "스타/스노우플레이크 스키마 설계",
                    "파티셔닝 전략 이해",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 3,
                "title": "Apache Spark 기초",
                "description": "대용량 데이터 분산 처리",
                "topics": ["Apache Spark", "PySpark", "RDD", "DataFrame", "Spark SQL"],
                "learning_objectives": [
                    "PySpark DataFrame API 활용",
                    "Spark 최적화 (파티션, 캐싱, 브로드캐스트)",
                    "Spark SQL로 대용량 쿼리 처리",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 4,
                "title": "Apache Kafka 스트리밍",
                "description": "실시간 데이터 파이프라인 구축",
                "topics": ["Kafka", "스트리밍", "실시간 처리", "토픽", "컨슈머 그룹", "Kafka Streams"],
                "learning_objectives": [
                    "Kafka Producer/Consumer 구현",
                    "실시간 이벤트 파이프라인 설계",
                    "Kafka Streams로 데이터 변환",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 5,
                "title": "데이터 파이프라인 오케스트레이션",
                "description": "Apache Airflow로 배치 파이프라인 관리",
                "topics": ["Apache Airflow", "DAG", "배치 처리", "파이프라인 오케스트레이션", "스케줄링"],
                "learning_objectives": [
                    "Airflow DAG 작성",
                    "의존성 있는 태스크 체인 구성",
                    "SLA 모니터링 및 알림 설정",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 6,
                "title": "클라우드 데이터 플랫폼",
                "description": "AWS/GCP 관리형 데이터 서비스 활용",
                "topics": ["AWS", "S3", "Glue", "Athena", "GCP", "BigQuery", "클라우드"],
                "learning_objectives": [
                    "S3 + Glue ETL 파이프라인 구성",
                    "BigQuery로 대용량 분석 쿼리 실행",
                    "클라우드 데이터 비용 최적화",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 7,
                "title": "데이터 품질 & 거버넌스",
                "description": "데이터 품질 관리와 메타데이터 관리",
                "topics": ["데이터 품질", "데이터 거버넌스", "메타데이터", "데이터 카탈로그", "Great Expectations"],
                "learning_objectives": [
                    "Great Expectations로 데이터 검증 작성",
                    "데이터 카탈로그 구성",
                    "데이터 리니지 추적",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 8,
                "title": "Docker & 인프라 기초",
                "description": "데이터 엔지니어가 알아야 할 컨테이너/인프라",
                "topics": ["Docker", "Docker Compose", "컨테이너", "인프라"],
                "learning_objectives": [
                    "Spark/Kafka 컨테이너 환경 구성",
                    "Docker Compose로 로컬 데이터 스택 구성",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 9,
                "title": "모니터링 & 관찰성",
                "description": "파이프라인 모니터링과 장애 대응",
                "topics": ["Prometheus", "Grafana", "로깅", "알림", "장애 대응"],
                "learning_objectives": [
                    "파이프라인 SLA 모니터링 대시보드 구성",
                    "장애 감지 및 알림 설정",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 10,
                "title": "팀 프로젝트: 엔드투엔드 파이프라인",
                "description": "실무형 데이터 파이프라인 팀 구축 실습",
                "topics": ["프로젝트", "협업", "엔드투엔드", "파이프라인 설계"],
                "learning_objectives": [
                    "요구사항 분석 → 파이프라인 설계 → 구현 → 운영 전 과정 경험",
                ],
                "estimated_hours": 24,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────────────
    # AI팀 / AI 엔지니어 / junior
    # ─────────────────────────────────────────────────────────────────
    {
        "department": "AI팀",
        "role": "AI 엔지니어",
        "career_level": "junior",
        "title": "AI 엔지니어 신입 정석 커리큘럼",
        "description": "신입 AI 엔지니어를 위한 ML/LLM/MLOps 12주 기초 과정",
        "total_weeks": 12,
        "modules": [
            {
                "week_number": 1,
                "title": "Python & 수학 기초",
                "description": "ML에 필요한 Python, 선형대수, 통계",
                "topics": ["Python", "numpy", "pandas", "선형대수", "통계", "matplotlib"],
                "learning_objectives": [
                    "numpy 배열 연산 능숙",
                    "기초 통계(평균, 분산, 상관관계) 계산",
                    "데이터 시각화",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 2,
                "title": "머신러닝 기초 (지도학습)",
                "description": "회귀, 분류, 모델 평가",
                "topics": ["머신러닝", "지도학습", "회귀", "분류", "scikit-learn", "교차검증", "과적합"],
                "learning_objectives": [
                    "scikit-learn으로 분류/회귀 모델 구축",
                    "교차검증, 하이퍼파라미터 튜닝",
                    "모델 평가지표(Accuracy, F1, AUC) 이해",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 3,
                "title": "딥러닝 기초 & PyTorch",
                "description": "신경망 원리와 PyTorch 실습",
                "topics": ["딥러닝", "PyTorch", "신경망", "역전파", "옵티마이저", "배치 정규화"],
                "learning_objectives": [
                    "PyTorch로 커스텀 모델 구현",
                    "역전파 및 경사하강법 이해",
                    "GPU 학습 환경 구성",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 4,
                "title": "Transformer & LLM 기초",
                "description": "Attention 메커니즘과 LLM 이해",
                "topics": ["Transformer", "Attention", "LLM", "GPT", "BERT", "사전학습", "파인튜닝"],
                "learning_objectives": [
                    "Self-Attention 메커니즘 수식 이해",
                    "사전학습/파인튜닝 개념 이해",
                    "HuggingFace Transformers 활용",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 5,
                "title": "LLM API 활용 & LangChain",
                "description": "OpenAI API와 LangChain으로 AI 애플리케이션 개발",
                "topics": ["OpenAI API", "LangChain", "프롬프트 엔지니어링", "체인", "에이전트"],
                "learning_objectives": [
                    "OpenAI API로 챗봇 구현",
                    "LangChain 체인/에이전트 구성",
                    "프롬프트 엔지니어링 기법 적용",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 6,
                "title": "RAG & 벡터 DB",
                "description": "검색 증강 생성(RAG) 파이프라인 구축",
                "topics": ["RAG", "벡터 DB", "Qdrant", "임베딩", "유사도 검색", "청킹"],
                "learning_objectives": [
                    "문서 임베딩 및 벡터 DB 저장",
                    "RAG 파이프라인 end-to-end 구현",
                    "청킹 전략 및 검색 품질 평가",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 7,
                "title": "모델 서빙 & FastAPI",
                "description": "ML 모델 REST API로 서빙",
                "topics": ["FastAPI", "모델 서빙", "REST API", "비동기", "성능 최적화"],
                "learning_objectives": [
                    "FastAPI로 ML 모델 API 구현",
                    "비동기 처리로 처리량 최적화",
                    "배치 추론 구현",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 8,
                "title": "MLOps 기초",
                "description": "모델 실험 관리와 배포 자동화",
                "topics": ["MLOps", "MLflow", "모델 레지스트리", "실험 관리", "CI/CD", "모델 배포"],
                "learning_objectives": [
                    "MLflow로 실험 추적 및 모델 버전 관리",
                    "모델 레지스트리 운영",
                    "CI/CD로 모델 배포 자동화",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 9,
                "title": "Docker & 컨테이너",
                "description": "AI 서비스 컨테이너화",
                "topics": ["Docker", "Dockerfile", "컨테이너", "GPU Docker", "최적화"],
                "learning_objectives": [
                    "ML 서비스 Dockerfile 최적화",
                    "GPU 컨테이너 환경 구성",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 10,
                "title": "모니터링 & 모델 드리프트",
                "description": "AI 서비스 운영 모니터링",
                "topics": ["모니터링", "Prometheus", "모델 드리프트", "데이터 드리프트", "A/B 테스트"],
                "learning_objectives": [
                    "모델 성능 모니터링 대시보드 구성",
                    "데이터/모델 드리프트 감지",
                    "A/B 테스트 설계",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 11,
                "title": "보안 & 윤리",
                "description": "AI 시스템 보안과 윤리적 고려사항",
                "topics": ["AI 보안", "프롬프트 인젝션", "AI 윤리", "편향", "데이터 프라이버시"],
                "learning_objectives": [
                    "프롬프트 인젝션 방어 기법",
                    "AI 편향 탐지 및 완화",
                    "개인정보보호 법규 이해",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 12,
                "title": "팀 프로젝트: AI 서비스 구축",
                "description": "엔드투엔드 AI 서비스 팀 프로젝트",
                "topics": ["프로젝트", "협업", "AI 서비스", "배포"],
                "learning_objectives": [
                    "기획 → 모델 → API → 배포 전 과정 경험",
                ],
                "estimated_hours": 24,
            },
        ],
    },

    # ─────────────────────────────────────────────────────────────────
    # 영업팀 / 영업사원 / junior
    # ─────────────────────────────────────────────────────────────────
    {
        "department": "영업팀",
        "role": "영업사원",
        "career_level": "junior",
        "title": "영업사원 신입 정석 커리큘럼",
        "description": "신입 영업사원을 위한 고객 발굴부터 계약 체결까지 12주 실전 영업 과정",
        "total_weeks": 12,
        "modules": [
            {
                "week_number": 1,
                "title": "회사 & 제품/서비스 이해",
                "description": "당사 제품/서비스 포트폴리오와 경쟁 우위 파악",
                "topics": ["제품 이해", "서비스 포트폴리오", "경쟁사 분석", "USP", "가치 제안"],
                "learning_objectives": [
                    "주요 제품/서비스별 핵심 가치 설명 가능",
                    "경쟁사 대비 차별점 3가지 이상 설명",
                    "고객 유형별 적합한 솔루션 매핑",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 2,
                "title": "영업 프로세스 기초",
                "description": "리드 발굴부터 계약까지 단계별 영업 사이클 이해",
                "topics": ["영업 프로세스", "리드 발굴", "콜드콜", "아웃바운드", "인바운드", "파이프라인 관리"],
                "learning_objectives": [
                    "영업 퍼널(Funnel) 단계 이해 및 설명",
                    "콜드콜 스크립트 작성 및 실습",
                    "리드 자격 심사(BANT) 수행",
                ],
                "estimated_hours": 16,
            },
            {
                "week_number": 3,
                "title": "CRM 시스템 활용",
                "description": "Salesforce/HubSpot 등 CRM 도구로 고객 관계 데이터 관리",
                "topics": ["CRM", "Salesforce", "HubSpot", "파이프라인", "리드 관리", "활동 로깅"],
                "learning_objectives": [
                    "CRM에 고객 정보 및 영업 활동 기록",
                    "파이프라인 단계 업데이트 및 예측",
                    "CRM 리포트로 개인 성과 분석",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 4,
                "title": "고객 커뮤니케이션 & 니즈 파악",
                "description": "고객과의 효과적 소통 및 잠재 니즈 발굴",
                "topics": ["고객 커뮤니케이션", "니즈 파악", "SPIN 기법", "경청", "질문 기술", "공감"],
                "learning_objectives": [
                    "SPIN(상황·문제·시사·욕구) 질문 기법 실습",
                    "고객의 명시적·잠재적 니즈 구분",
                    "적극적 경청 스킬 적용",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 5,
                "title": "프레젠테이션 & 제품 데모 스킬",
                "description": "설득력 있는 프레젠테이션과 제품 시연 기술",
                "topics": ["프레젠테이션", "제품 데모", "스토리텔링", "시각 자료", "PPT", "Q&A 대응"],
                "learning_objectives": [
                    "고객 맞춤형 PPT 제작 및 발표",
                    "제품 데모 시나리오 구성 및 시연",
                    "예상 반론에 대한 Q&A 대응",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 6,
                "title": "협상 & 가격 조율",
                "description": "상호 이익을 위한 협상 전략과 가격 협의 기술",
                "topics": ["협상", "가격 협의", "BATNA", "양보 전략", "가치 기반 가격", "할인 정책"],
                "learning_objectives": [
                    "BATNA(최선의 대안) 설정 및 활용",
                    "가치 기반 가격 협상 실습",
                    "할인 요청 시 대응 전략 수립",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 7,
                "title": "제안서 & 계약서 작성",
                "description": "고객 맞춤형 제안서 및 계약 문서 작성",
                "topics": ["제안서", "RFP", "계약서", "SOW", "법적 검토", "조건 협의"],
                "learning_objectives": [
                    "RFP 분석 후 맞춤 제안서 작성",
                    "SOW(작업 기술서) 핵심 항목 이해",
                    "계약 조건 협의 포인트 파악",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 8,
                "title": "클로징 전략",
                "description": "효과적인 계약 체결 기술과 반론 극복",
                "topics": ["클로징", "반론 극복", "클로징 기법", "타임라인 설정", "의사결정 촉진"],
                "learning_objectives": [
                    "다양한 클로징 기법 적용 (Trial, Summary, Urgency)",
                    "반론 유형별 대응 스크립트 작성",
                    "의사결정자 접근 전략 수립",
                ],
                "estimated_hours": 12,
            },
            {
                "week_number": 9,
                "title": "시장 분석 & 타겟 고객 발굴",
                "description": "시장 세분화와 이상적 고객 프로파일(ICP) 정의",
                "topics": ["시장 분석", "시장 세분화", "ICP", "페르소나", "경쟁 분석", "TAM/SAM/SOM"],
                "learning_objectives": [
                    "ICP(이상적 고객 프로파일) 정의",
                    "시장 세분화 및 타겟 리스트 작성",
                    "경쟁 분석 매트릭스 작성",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 10,
                "title": "영업 데이터 분석 & KPI 관리",
                "description": "영업 지표 분석과 성과 개선",
                "topics": ["영업 KPI", "전환율", "평균 거래 규모", "영업 사이클", "데이터 분석", "Excel", "대시보드"],
                "learning_objectives": [
                    "핵심 영업 KPI (전환율, ARR, 파이프라인 커버리지) 이해",
                    "Excel/스프레드시트로 영업 실적 분석",
                    "주간 영업 보고서 작성",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 11,
                "title": "고객 유지 & 사후 관리",
                "description": "기존 고객 관계 강화와 업셀/크로스셀 기회 발굴",
                "topics": ["고객 유지", "사후 관리", "업셀", "크로스셀", "재계약", "NPS", "고객 성공"],
                "learning_objectives": [
                    "계약 후 온보딩 프로세스 진행",
                    "업셀/크로스셀 기회 탐색 방법",
                    "NPS 설문 분석 및 개선 액션 수립",
                ],
                "estimated_hours": 8,
            },
            {
                "week_number": 12,
                "title": "팀 프로젝트: 실전 영업 시뮬레이션",
                "description": "실제 영업 시나리오 기반 팀 롤플레이 및 피드백",
                "topics": ["롤플레이", "실전 시뮬레이션", "팀 협업", "영업 발표", "피드백"],
                "learning_objectives": [
                    "리드 발굴 → 제안 → 협상 → 클로징 전 과정 팀 시뮬레이션",
                    "동료 피드백 수렴 및 개선점 도출",
                ],
                "estimated_hours": 24,
            },
        ],
    },
]


def seed(payload: dict) -> bool:
    try:
        resp = requests.post(URL, json=payload, timeout=30)
        if resp.status_code in (200, 201):
            data = resp.json().get("data", {})
            print(f"  [OK] {payload['department']} / {payload['role']} / {payload['career_level']}"
                  f" → {len(data.get('modules', []))}개 모듈")
            return True
        else:
            print(f"  [FAIL] HTTP {resp.status_code} — {resp.text[:300]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  [FAIL] 연결 실패 — {URL}")
        return False
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


FILTER_MAP = {
    "ai":    "AI팀",
    "sales": "영업팀",
    "dev":   "개발팀",
    "data":  "데이터팀",
}


if __name__ == "__main__":
    # 선택적 부서 필터 (예: python seed_standard_curriculums.py ai sales)
    dept_filter = {FILTER_MAP[k] for k in sys.argv[1:] if k in FILTER_MAP}
    targets = [sc for sc in STANDARD_CURRICULUMS if not dept_filter or sc["department"] in dept_filter]

    print("=" * 55)
    print("  부서별 정석 커리큘럼 초기 데이터 투입")
    print(f"  endpoint: {URL}")
    if dept_filter:
        print(f"  대상 부서: {', '.join(dept_filter)}")
    print("=" * 55)

    results = [seed(sc) for sc in targets]

    print()
    print(f"  결과: {sum(results)}/{len(results)} 성공")
    if not all(results):
        print("  실패한 항목의 로그 확인:")
        print("    docker compose logs curriculum-designer-agent --tail 30")
        sys.exit(1)
    else:
        print("  완료! 확인:")
        print(f"    GET {BASE}/curriculums/standard")
