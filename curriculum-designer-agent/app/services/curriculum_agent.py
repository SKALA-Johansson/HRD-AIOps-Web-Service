"""
Curriculum Designer Agent (RAG 기반)
교육 목표를 분석하고, Qdrant에서 관련 교육 자료를 검색하여
맞춤형 커리큘럼과 주차별 모듈 콘텐츠를 생성합니다.
"""
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.rag.qdrant_client import search_relevant_content

logger = logging.getLogger(__name__)

CURRICULUM_SYSTEM_PROMPT = """당신은 기업 교육 커리큘럼을 설계하는 전문 AI 에이전트입니다.
직원의 프로필과 학습 목표를 분석하고, 제공된 참고 자료를 활용하여
체계적인 교육 커리큘럼을 설계합니다.

반드시 아래 JSON 형식으로 응답하세요 (다른 텍스트 없이 JSON만):
{
  "title": "커리큘럼 제목",
  "description": "커리큘럼 전체 설명",
  "total_weeks": 전체주차수,
  "skill_analysis": {
    "detected_skills": ["직원이 보유한 스킬1", "스킬2"],
    "decisions": [
      {
        "module_title": "모듈명",
        "action": "INCLUDE",
        "reason": "보유 역량 없음 - 필수 학습 필요"
      },
      {
        "module_title": "모듈명",
        "action": "EXCLUDE",
        "reason": "SQL 기초 역량 보유 - 제외"
      },
      {
        "module_title": "모듈명",
        "action": "ADVANCED",
        "reason": "Python 기초 보유 - 심화 과정으로 전환"
      }
    ]
  },
  "modules": [
    {
      "week_number": 1,
      "title": "모듈 제목",
      "description": "모듈 설명",
      "content": "학습 내용 (마크다운 형식)",
      "learning_objectives": ["학습 목표1", "학습 목표2"],
      "resources": ["참고자료1", "참고자료2"],
      "assignments": ["과제1", "과제2"],
      "estimated_hours": 8
    }
  ]
}"""

MODULE_SYSTEM_PROMPT = """당신은 기업 교육 콘텐츠를 생성하는 전문 AI 에이전트입니다.
주어진 학습 목표와 참고 자료를 바탕으로 실무에 바로 적용 가능한
상세한 교육 콘텐츠를 마크다운 형식으로 작성합니다.

콘텐츠 구성:
1. 학습 목표
2. 핵심 개념 설명
3. 실습 예제
4. 적용 방법
5. 점검 문제"""


def _format_content_catalog(content_catalog: list[dict] | None, limit: int = 25) -> str:
    if not content_catalog:
        return "- 등록된 교육 콘텐츠 없음"

    rows: list[str] = []
    for content in content_catalog[:limit]:
        title = str(content.get("title") or "").strip()
        if not title:
            continue
        category = str(content.get("category") or "").strip() or "미분류"
        tags = content.get("tags") or []
        tag_text = ", ".join([str(t).strip() for t in tags if str(t).strip()][:5]) or "-"
        rows.append(f"- {title} | category={category} | tags={tag_text}")

    return "\n".join(rows) if rows else "- 등록된 교육 콘텐츠 없음"


def _format_module_content_map(module_content_map: dict[str, list[dict]] | None, limit: int = 20) -> str:
    if not module_content_map:
        return "- 모듈별 매칭 정보 없음"

    rows: list[str] = []
    count = 0
    for module_title, matches in module_content_map.items():
        if count >= limit:
            break
        match_text = ", ".join(
            [str(m.get("title") or "").strip() for m in (matches or []) if str(m.get("title") or "").strip()][:3]
        ) or "없음"
        rows.append(f"- {module_title}: {match_text}")
        count += 1
    return "\n".join(rows) if rows else "- 모듈별 매칭 정보 없음"


class CurriculumDesignerAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )

    async def design_curriculum(
        self,
        employee_name: str,
        department: str,
        role: str,
        career_level: str,
        experience_years: int,
        skills: list[str],
        goals: list[dict],
        content_catalog: list[dict] | None = None,
    ) -> dict:
        """RAG를 활용하여 맞춤형 커리큘럼을 생성합니다."""
        goal_titles = [g.get("title", "") for g in goals]
        rag_query = f"{role} {department} {' '.join(goal_titles)}"
        try:
            rag_context = await search_relevant_content(rag_query, k=5)
            rag_text = "\n\n".join(rag_context) if rag_context else "참고 자료 없음"
        except Exception as e:
            logger.warning(f"[RAG] 검색 실패: {e}")
            rag_text = "참고 자료 없음"

        goals_text = "\n".join([
            f"- [{g.get('priority','').upper()}] {g.get('title','')} "
            f"(기간: {g.get('duration_weeks',4)}주, "
            f"습득 스킬: {', '.join(g.get('skills_to_learn', []))})"
            for g in goals
        ])

        career_map = {"junior": "신입/주니어", "mid": "미드레벨", "senior": "시니어"}
        level_label = career_map.get(career_level, career_level)
        content_catalog_text = _format_content_catalog(content_catalog)
        skills_text = ", ".join(skills) if skills else "없음"

        user_message = f"""다음 직원을 위한 교육 커리큘럼을 설계해주세요:

[직원 정보]
- 이름: {employee_name}
- 부서: {department}
- 역할: {role}
- 경력 수준: {level_label} ({experience_years}년)
- 보유 스킬: {skills_text}

[역량 시맨틱 추론 규칙 - 반드시 적용]
- Oracle, MySQL, MariaDB, PostgreSQL, SQLite, MSSQL 중 하나라도 있으면 → SQL 기초 보유
- Spring, Django, FastAPI, Express 등 웹 프레임워크 → 해당 언어 기초 보유
- TensorFlow, PyTorch, Keras → 머신러닝/딥러닝 기초 보유
- Kubernetes, Docker → 컨테이너/인프라 기초 보유

[현재 등록된 교육 콘텐츠 목록 - 판단 대상]
아래 콘텐츠 각각에 대해 이 직원에게 필요한지 판단하세요:
{content_catalog_text}

[교육 목표]
{goals_text}

[참고 교육 자료]
{rag_text[:2000]}

[역량 기반 포함 판단 규칙 - 반드시 준수]
1. 보유 스킬과 시맨틱 추론을 바탕으로 직원이 이미 아는 내용을 파악하세요.
2. 등록된 교육 콘텐츠 각각에 대해 판단하세요:
   - 직원이 해당 내용을 모른다면 → action: INCLUDE
   - 이미 기초를 안다면 → action: EXCLUDE (reason에 구체적 근거)
   - 기초는 알지만 심화 필요 → action: ADVANCED
3. skill_analysis.detected_skills에 보유 역량 + 시맨틱 추론 확장 역량을 모두 기록하세요.
4. skill_analysis.decisions에 각 콘텐츠에 대한 판단을 빠짐없이 기록하세요.
   (module_title에 콘텐츠 제목 그대로 사용)
5. modules에는 INCLUDE/ADVANCED 콘텐츠만 포함하고 week_number를 1부터 부여하세요.
6. 반드시 JSON 형식으로만 응답하세요."""

        messages = [
            SystemMessage(content=CURRICULUM_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)

    async def generate_module_content(
        self,
        module_title: str,
        learning_objectives: list[str],
        role: str,
        department: str,
    ) -> str:
        """특정 모듈의 상세 교육 콘텐츠를 RAG 기반으로 생성합니다."""
        rag_query = f"{module_title} {role} {department}"
        try:
            rag_context = await search_relevant_content(rag_query, k=3)
            rag_text = "\n\n".join(rag_context) if rag_context else ""
        except Exception:
            rag_text = ""

        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives])
        rag_section = f"참고 자료:\n{rag_text[:2000]}" if rag_text else ""

        user_message = f"""다음 모듈의 상세 교육 콘텐츠를 작성해주세요:

모듈명: {module_title}
대상: {department} {role}

학습 목표:
{objectives_text}

{rag_section}

마크다운 형식으로 실무 중심의 학습 콘텐츠를 작성해주세요."""

        messages = [
            SystemMessage(content=MODULE_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        return response.content.strip()

    async def revise_curriculum(
        self,
        current_curriculum: dict,
        revision_note: str,
    ) -> dict:
        """피드백을 반영하여 커리큘럼을 수정합니다."""
        user_message = f"""다음 커리큘럼을 수정 요청사항에 맞게 개선해주세요:

[현재 커리큘럼]
제목: {current_curriculum.get('title')}
설명: {current_curriculum.get('description')}
모듈 수: {len(current_curriculum.get('modules', []))}주

[수정 요청]
{revision_note}

전체 커리큘럼을 수정하여 JSON 형식으로 반환해주세요."""

        messages = [
            SystemMessage(content=CURRICULUM_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)

    async def design_personalized_curriculum(
        self,
        standard_modules: list[dict],
        employee_name: str,
        department: str,
        role: str,
        career_level: str,
        existing_skills: list[str],
        goals: list[dict],
        content_catalog: list[dict] | None = None,
        module_content_map: dict[str, list[dict]] | None = None,
    ) -> dict:
        """
        정석 커리큘럼 모듈 목록을 기반으로 맞춤 커리큘럼을 생성합니다.

        규칙:
        - PDF에서 추출한 보유 역량에 없는 모듈 → 반드시 포함 (INCLUDE)
        - 보유 역량과 겹치는 모듈 → AI가 포함(심화)/제외 판단 (ADVANCED / EXCLUDE)
        """
        goal_titles = [g.get("title", "") for g in goals]
        rag_query = f"{role} {department} {' '.join(goal_titles)}"
        try:
            rag_context = await search_relevant_content(rag_query, k=5)
            rag_text = "\n\n".join(rag_context) if rag_context else "참고 자료 없음"
        except Exception as e:
            logger.warning(f"[RAG] 검색 실패: {e}")
            rag_text = "참고 자료 없음"

        standard_modules_text = "\n".join([
            f"  Week {m['week_number']}: {m['title']} "
            f"[topics: {', '.join(m.get('topics', []))}]"
            for m in standard_modules
        ])

        existing_skills_text = ", ".join(existing_skills) if existing_skills else "없음"
        goals_text = "\n".join([f"- {g.get('title', '')}" for g in goals])
        career_map = {"junior": "신입/주니어", "mid": "미드레벨", "senior": "시니어"}
        level_label = career_map.get(career_level, career_level)
        content_catalog_text = _format_content_catalog(content_catalog)
        module_content_text = _format_module_content_map(module_content_map)

        user_message = f"""다음 직원을 위한 맞춤형 커리큘럼을 설계해주세요.

[직원 정보]
- 이름: {employee_name}
- 부서: {department}
- 역할: {role}
- 경력 수준: {level_label}
- PDF에서 추출한 보유 역량: {existing_skills_text}

[역량 시맨틱 추론 규칙 - 반드시 적용]
아래 역량 보유 시 관련 기초 지식도 보유한 것으로 간주합니다:
- Oracle, MySQL, MariaDB, PostgreSQL, SQLite, MSSQL 중 하나라도 있으면 → SQL 기초 보유
- Spring, Django, FastAPI, Express 등 웹 프레임워크 → 해당 언어 기초 보유
- TensorFlow, PyTorch, Keras → 머신러닝/딥러닝 기초 보유
- Kubernetes, Docker → 컨테이너/인프라 기초 보유

[부서 표준 커리큘럼 모듈 목록 - 판단 대상]
아래는 {department} 부서 신입사원이 반드시 이수해야 하는 표준 커리큘럼입니다.
각 모듈에 대해 이 직원에게 필요한지 판단하세요:
{standard_modules_text}

[교육 목표]
{goals_text}

[참고 교육 자료 (RAG)]
{rag_text[:2000]}

[역량 기반 포함 판단 규칙 - 반드시 준수]
1. 보유 역량 목록과 시맨틱 추론 결과를 바탕으로 직원이 이미 아는 내용을 파악하세요.
2. 위 [부서 표준 커리큘럼 모듈 목록]의 각 모듈에 대해 판단하세요:
   - 직원이 해당 내용을 모른다면 → action: INCLUDE (커리큘럼에 필수 포함)
   - 직원이 이미 기초를 안다면 → action: EXCLUDE (제외, reason에 구체적 근거)
   - 기초는 알지만 심화가 필요하다면 → action: ADVANCED (심화 과정으로 포함)
3. skill_analysis.detected_skills에 보유 역량 + 시맨틱 추론으로 확장된 역량을 모두 기록하세요.
4. skill_analysis.decisions에 표준 모듈 각각에 대한 판단을 빠짐없이 기록하세요.
   (module_title에 표준 모듈 제목 그대로 사용)
5. modules 배열에는 INCLUDE/ADVANCED로 판단된 모듈만 포함하고 week_number를 1부터 부여하세요.
6. EXCLUDE된 모듈은 modules에 포함하지 마세요.
7. 반드시 JSON 형식으로만 응답하세요."""

        messages = [
            SystemMessage(content=CURRICULUM_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)


curriculum_designer_agent = CurriculumDesignerAgent()
