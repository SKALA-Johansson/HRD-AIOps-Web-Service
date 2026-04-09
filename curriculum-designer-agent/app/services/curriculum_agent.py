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

반드시 아래 JSON 형식으로 응답하세요:
{{
  "title": "커리큘럼 제목",
  "description": "커리큘럼 전체 설명",
  "total_weeks": 전체주차수,
  "modules": [
    {{
      "week_number": 1,
      "title": "모듈 제목",
      "description": "모듈 설명",
      "content": "학습 내용 (마크다운 형식)",
      "learning_objectives": ["학습 목표1", "학습 목표2"],
      "resources": ["참고자료1", "참고자료2"],
      "assignments": ["과제1", "과제2"],
      "estimated_hours": 시간수
    }}
  ]
}}"""

MODULE_SYSTEM_PROMPT = """당신은 기업 교육 콘텐츠를 생성하는 전문 AI 에이전트입니다.
주어진 학습 목표와 참고 자료를 바탕으로 실무에 바로 적용 가능한
상세한 교육 콘텐츠를 마크다운 형식으로 작성합니다.

콘텐츠 구성:
1. 학습 목표
2. 핵심 개념 설명
3. 실습 예제
4. 적용 방법
5. 점검 문제"""


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
    ) -> dict:
        """
        RAG를 활용하여 맞춤형 커리큘럼을 생성합니다.
        """
        # 1. RAG: 관련 교육 자료 검색
        goal_titles = [g.get("title", "") for g in goals]
        rag_query = f"{role} {department} {' '.join(goal_titles)}"
        try:
            rag_context = await search_relevant_content(rag_query, k=5)
            rag_text = "\n\n".join(rag_context) if rag_context else "참고 자료 없음"
        except Exception as e:
            logger.warning(f"[RAG] 검색 실패: {e}")
            rag_text = "참고 자료 없음"

        # 2. 교육 목표 정리
        goals_text = "\n".join([
            f"- [{g.get('priority','').upper()}] {g.get('title','')} "
            f"(기간: {g.get('duration_weeks',4)}주, "
            f"습득 스킬: {', '.join(g.get('skills_to_learn', []))})"
            for g in goals
        ])

        career_map = {"junior": "신입/주니어", "mid": "미드레벨", "senior": "시니어"}
        level_label = career_map.get(career_level, career_level)

        user_message = f"""다음 직원을 위한 교육 커리큘럼을 설계해주세요:

[직원 정보]
- 이름: {employee_name}
- 부서: {department}
- 역할: {role}
- 경력 수준: {level_label} ({experience_years}년)
- 보유 스킬: {', '.join(skills) if skills else '없음'}

[교육 목표]
{goals_text}

[참고 교육 자료]
{rag_text[:3000]}

위 정보를 바탕으로 주차별 모듈이 포함된 교육 커리큘럼을 JSON 형식으로 생성해주세요."""

        messages = [
            SystemMessage(content=CURRICULUM_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        # JSON 파싱
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
        """
        특정 모듈의 상세 교육 콘텐츠를 RAG 기반으로 생성합니다.
        """
        # RAG 검색
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
        """
        피드백을 반영하여 커리큘럼을 수정합니다.
        """
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


curriculum_designer_agent = CurriculumDesignerAgent()
