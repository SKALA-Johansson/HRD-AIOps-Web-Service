"""
Qdrant 초기 데이터 투입 스크립트

사용법:
  python seed_qdrant.py

전제:
  - docker-compose up 으로 서비스들이 기동된 상태
  - Gateway: http://localhost:8080
"""

import requests
import json
import sys

GATEWAY = "http://localhost:8080"

# ──────────────────────────────────────────────────────────────────────────────
# curriculum_rag: 커리큘럼 설계 / 교육 콘텐츠 참고 자료
# ──────────────────────────────────────────────────────────────────────────────
CURRICULUM_DOCS = {
    "texts": [
        """[직무역량 교육과정 설계 원칙]
효과적인 교육과정은 학습자의 현재 역량 수준(AS-IS)과 목표 역량 수준(TO-BE)의 차이를 분석하여 설계합니다.
주니어(0-2년): 기초 이론과 도구 사용법 중심, 주 8시간 이내 학습 권장
미드레벨(3-5년): 실무 프로젝트 기반 학습, 사례 연구 포함
시니어(6년+): 리더십, 아키텍처 설계, 멘토링 역량 개발""",

        """[소프트웨어 엔지니어링 교육 모듈 구성]
Week 1-2: 프로그래밍 기초 및 알고리즘
  - 자료구조: 배열, 링크드리스트, 트리, 그래프
  - 정렬 알고리즘: Quick Sort, Merge Sort, Heap Sort
  - 시간/공간 복잡도 분석 (Big-O)
Week 3-4: 객체지향 설계 원칙
  - SOLID 원칙 (단일책임, 개방폐쇄, 리스코프치환, 인터페이스분리, 의존역전)
  - 디자인 패턴: Singleton, Factory, Observer, Strategy
Week 5-6: 데이터베이스 설계
  - 관계형 DB 정규화 (1NF~3NF)
  - SQL 최적화, 인덱싱 전략
  - NoSQL 선택 기준 (Document, Key-Value, Graph)""",

        """[MLOps / AI 엔지니어링 교육 커리큘럼]
Week 1-3: ML 기초 — 지도학습, 비지도학습, 강화학습, scikit-learn 실습
Week 4-6: 딥러닝 — PyTorch, CNN, RNN, Transformer 아키텍처
Week 7-9: LLM & RAG
  - OpenAI API 활용
  - LangChain 체인 구성
  - Qdrant 벡터 DB 활용 및 RAG 파이프라인 구축
Week 10-12: MLOps — 모델 서빙(FastAPI), CI/CD(MLflow), 모니터링(Prometheus, Grafana)""",

        """[데이터 엔지니어링 교육 과정]
Week 1-2: 데이터 웨어하우스 — OLTP vs OLAP, 스타/스노우플레이크 스키마, 파티셔닝
Week 3-4: Apache Spark — RDD, DataFrame, Spark SQL, Catalyst 옵티마이저
Week 5-6: 스트리밍 처리 — Apache Kafka(토픽, 파티션, 컨슈머 그룹), Spark Streaming, Flink
Week 7-8: 클라우드 데이터 플랫폼
  - AWS: S3, Glue, Athena, Redshift
  - GCP: BigQuery, Dataflow, Pub/Sub""",

        """[DevOps / 클라우드 인프라 교육]
Week 1-2: 컨테이너 — Docker 이미지 최적화(멀티스테이지 빌드), Docker Compose
Week 3-4: 쿠버네티스 — Pod, Deployment, Service, Ingress, HPA
Week 5-6: CI/CD — GitHub Actions 워크플로우, ArgoCD GitOps
Week 7-8: 모니터링 & 관찰성
  - Prometheus + Grafana 대시보드
  - ELK Stack (로그 수집/분석)
  - 분산 추적 (Jaeger, Zipkin)""",

        """[마이크로서비스 아키텍처 교육]
핵심 개념:
- 서비스 분리: DDD 바운디드 컨텍스트
- 통신 패턴: 동기(REST, gRPC) vs 비동기(Kafka, RabbitMQ)
- 서비스 디스커버리: Eureka, Consul
- API 게이트웨이: Spring Cloud Gateway, Kong
- 분산 트랜잭션: Saga 패턴 (Choreography vs Orchestration)
- 서킷 브레이커: Resilience4j
학습 결과물: 3개 이상 마이크로서비스 + Kafka 이벤트 드리븐 아키텍처 샘플 구현""",
    ],
    "metadatas": [
        {"category": "curriculum_design", "level": "all"},
        {"category": "software_engineering", "weeks": "1-6"},
        {"category": "ai_ml", "weeks": "1-12"},
        {"category": "data_engineering", "weeks": "1-8"},
        {"category": "devops", "weeks": "1-8"},
        {"category": "architecture", "topic": "microservices"},
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# tutor_rag: AI 튜터가 질문 답변 시 참조하는 기술 Q&A 지식 베이스
# ──────────────────────────────────────────────────────────────────────────────
TUTOR_DOCS = {
    "texts": [
        """Q: Python에서 async/await를 사용해야 하는 경우는 언제인가요?
A: I/O 바운드 작업(HTTP 요청, DB 쿼리, 파일 읽기)이 많을 때 사용합니다.
CPU 바운드 작업은 asyncio가 도움이 되지 않으며 multiprocessing을 고려해야 합니다.
FastAPI, aiohttp 같은 비동기 프레임워크와 함께 사용할 때 효과가 큽니다.
주의: 동기 함수를 async 함수에서 직접 호출하면 이벤트 루프가 블로킹됩니다.
해결책: asyncio.run_in_executor()로 동기 함수를 스레드풀에서 실행하세요.""",

        """Q: RAG(Retrieval-Augmented Generation)의 작동 원리를 설명해주세요.
A: RAG는 두 단계로 동작합니다.
1. Retrieval(검색): 사용자 질문을 임베딩 벡터로 변환 후, 벡터 DB에서 코사인 유사도로 검색
2. Generation(생성): 검색된 문서를 컨텍스트로 LLM에게 전달하여 답변 생성
장점: LLM 지식 한계 보완, 환각(Hallucination) 감소, 출처 추적 가능
구현 스택: LangChain + Qdrant + OpenAI Embeddings
핵심 파라미터: chunk_size(문서 분할 크기), k(검색 문서 수)""",

        """Q: Docker 컨테이너가 계속 재시작되는 경우 디버깅 방법은?
A:
1. 로그 확인: docker logs <container_name> --tail 50
2. 종료 코드 확인: docker inspect <container_name> | grep ExitCode
   - ExitCode 1: 애플리케이션 오류 / ExitCode 137: OOM Killer / ExitCode 143: SIGTERM
3. 실시간 이벤트: docker events --filter container=<name>
4. 컨테이너 내부 진입: docker exec -it <container_name> /bin/sh
5. 헬스체크 상태: docker inspect --format='{{json .State.Health}}' <container_name>""",

        """Q: Kafka에서 컨슈머 그룹을 사용해야 하는 이유는?
A: 컨슈머 그룹은 여러 컨슈머가 협력하여 토픽의 파티션을 나누어 처리합니다.
핵심 원리: 하나의 파티션은 그룹 내 하나의 컨슈머만 읽음 (병렬 처리 보장)
확장 전략: 처리량 증가 → 컨슈머 인스턴스 추가 (파티션 수까지)
오프셋 관리:
- enable.auto.commit=true: 자동 커밋 (메시지 손실 가능)
- enable.auto.commit=false: 처리 완료 후 수동 커밋 (권장)
group_id 설계: 서비스별 독립 group_id 사용 (예: curriculum-designer-group, ai-tutor-group)""",

        """Q: SQL 쿼리 성능을 개선하는 방법을 알려주세요.
A:
1. 인덱스 활용: WHERE, JOIN, ORDER BY 컬럼에 인덱스 생성. EXPLAIN ANALYZE로 실행 계획 확인
2. 쿼리 최적화: SELECT * 대신 필요 컬럼만 선택. N+1 문제 → JOIN으로 해결
3. 페이지네이션: LIMIT/OFFSET → 커서 기반 페이지네이션으로 대체
4. 데이터 모델: 읽기 많은 테이블은 비정규화 고려. 날짜 기준 Range 파티션 활용
5. 캐싱: 자주 조회되는 결과 → Redis 캐시 (TTL 및 무효화 전략 필요)""",

        """Q: Spring Boot에서 @Transactional이 작동하지 않는 원인은?
A:
1. self-invocation 문제: 같은 클래스 내 @Transactional 메서드 직접 호출 시 프록시 우회
   해결: 별도 서비스 빈으로 분리
2. 예외 타입: 기본값은 RuntimeException만 롤백. Checked Exception은 무시됨
   해결: @Transactional(rollbackFor = Exception.class)
3. 접근 제어자: private 메서드에 적용 불가. public만 가능
4. 비동기 처리: @Async와 함께 사용 시 트랜잭션 컨텍스트 전파 안 됨
5. readOnly = true 설정 시 쓰기 시도하면 오류 발생""",

        """Q: 학습 중 막히는 개념이 있을 때 효과적인 학습 전략은?
A:
1. 파인만 기법: 이해한 내용을 초등학생에게 설명하듯 글로 써보세요. 설명 못하는 부분 = 진짜 모르는 부분
2. 분할 정복: 막히는 개념을 더 작은 단위로 나눠서 각각 이해
   예) "Kafka 이해 안됨" → "메시지큐란?" → "파티션이란?" → "오프셋이란?"
3. 실습 우선: 공식 문서 Quick Start부터 동작하는 코드 만들기
4. 공식 문서 활용: 블로그보다 공식 문서가 정확 (docs.python.org, docs.spring.io)
5. 검색어를 영어로 바꾸면 10배 이상 자료를 찾을 수 있음""",

        """Q: MSA 환경에서 분산 트레이싱을 구현하는 방법은?
A:
핵심 개념:
- Trace: 하나의 요청 전체 흐름 (TraceId로 식별)
- Span: 개별 서비스 처리 단위 (SpanId로 식별)
- Context Propagation: HTTP 헤더(B3, W3C TraceContext)로 트레이스 정보 전달

구현 방법 (Spring Boot):
- Micrometer Tracing + Zipkin: spring-boot-starter-actuator 활용, 자동 HTTP 계측
- OpenTelemetry (권장): -javaagent:opentelemetry-javaagent.jar (코드 수정 없음)

FastAPI:
- opentelemetry-instrumentation-fastapi 패키지 사용

Kafka 메시지 트레이싱: 메시지 헤더에 TraceId 포함하여 비동기 흐름도 추적 가능""",
    ],
    "metadatas": [
        {"category": "python", "topic": "async", "type": "qa"},
        {"category": "ai_ml", "topic": "rag", "type": "qa"},
        {"category": "devops", "topic": "docker", "type": "qa"},
        {"category": "kafka", "topic": "consumer_group", "type": "qa"},
        {"category": "database", "topic": "sql_optimization", "type": "qa"},
        {"category": "spring_boot", "topic": "transaction", "type": "qa"},
        {"category": "learning_strategy", "type": "general"},
        {"category": "architecture", "topic": "distributed_tracing", "type": "qa"},
    ],
}


def post_documents(url: str, payload: dict, label: str) -> bool:
    try:
        resp = requests.post(url, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            uploaded = data.get("data", {}).get("uploaded", "?")
            print(f"  ✓ {label}: {uploaded}건 저장 완료")
            return True
        else:
            print(f"  ✗ {label}: HTTP {resp.status_code} — {resp.text[:300]}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"  ✗ {label}: 연결 실패 — {url} 에 접근할 수 없습니다. 서비스가 기동 중인지 확인하세요.")
        return False
    except Exception as e:
        print(f"  ✗ {label}: 오류 — {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("  Qdrant 초기 데이터 투입")
    print(f"  Gateway: {GATEWAY}")
    print("=" * 50)
    print()

    ok1 = post_documents(
        url=f"{GATEWAY}/api/v1/curriculums/rag/documents",
        payload=CURRICULUM_DOCS,
        label="curriculum_rag",
    )

    ok2 = post_documents(
        url=f"{GATEWAY}/api/v1/tutor/rag/documents",
        payload=TUTOR_DOCS,
        label="tutor_rag",
    )

    print()
    if ok1 and ok2:
        print("모든 데이터 투입 완료!")
        print("Qdrant 대시보드에서 확인: http://localhost:6333/dashboard")
    else:
        print("일부 투입 실패 — 서비스 로그를 확인하세요.")
        sys.exit(1)
