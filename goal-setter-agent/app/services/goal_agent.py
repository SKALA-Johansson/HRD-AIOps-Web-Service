"""
Goal Setter Agent
신입사원 프로필을 분석하여 개인별 교육 목표를 자동으로 생성합니다.
LangChain + OpenAI 기반 Agentic AI
"""
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.schemas.goal import LearningGoalItem

logger = logging.getLogger(__name__)


PROFILE_EXTRACT_PROMPT = """당신은 신입사원 지원서/이력서 PDF에서 정보를 추출하는 AI입니다.
주어진 텍스트에서 다음 정보를 추출하여 반드시 JSON 형식으로 반환하세요.
찾을 수 없는 항목은 기본값을 사용하세요.

반환 형식:
{
  "employee_name": "이름 (없으면 '미상')",
  "department": "부서명 (없으면 '미분류')",
  "role": "직무/직책 (없으면 '신입')",
  "career_level": "junior 또는 mid 또는 senior (경력 연수 기준: 0-2년=junior, 3-5년=mid, 6년+=senior)",
  "experience_years": 경력 연수 숫자 (없으면 0),
  "skills": ["보유 스킬1", "보유 스킬2", ...]
}"""

SYSTEM_PROMPT = """당신은 신입사원 교육 목표를 설정하는 전문 HR AI 에이전트입니다.
신입사원의 프로필(부서, 역할, 경력 수준, 보유 스킬, 경력 연수)을 분석하여
개인에게 최적화된 교육 목표를 생성해야 합니다.

교육 목표 생성 기준:
1. 역할과 부서에 맞는 핵심 역량 강화
2. 부족한 스킬 파악 및 보완
3. 경력 수준에 맞는 난이도 조절
4. 단기(1-4주), 중기(5-8주), 장기(9-12주) 목표 균형
5. 측정 가능한 성공 기준 설정

반드시 아래 JSON 배열 형식으로 응답하세요 (한국어):
[
  {{
    "title": "목표 제목",
    "description": "상세 설명",
    "priority": "high|medium|low",
    "duration_weeks": 숫자,
    "skills_to_learn": ["스킬1", "스킬2"],
    "success_criteria": "성공 기준"
  }}
]

3~5개의 교육 목표를 생성하세요."""


class GoalSetterAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )
        self.parser = JsonOutputParser()

    async def generate_goals(
        self,
        employee_id: str,
        employee_name: str,
        department: str,
        role: str,
        career_level: str,
        experience_years: int,
        skills: list[str],
    ) -> list[dict]:
        """
        직원 프로필을 기반으로 AI가 학습 목표를 생성합니다.
        """
        career_map = {"junior": "신입/주니어 (0-2년)", "mid": "미드레벨 (3-5년)", "senior": "시니어 (6년+)"}
        level_label = career_map.get(career_level, career_level)
        skills_str = ", ".join(skills) if skills else "없음"

        user_message = f"""다음 신입사원의 교육 목표를 생성해주세요:

- 이름: {employee_name}
- 부서: {department}
- 역할(직책): {role}
- 경력 수준: {level_label}
- 경력 연수: {experience_years}년
- 보유 스킬: {skills_str}

위 프로필을 분석하여 이 직원에게 최적화된 교육 목표를 JSON 배열로 생성해주세요."""

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        # JSON 파싱 (마크다운 코드블록 제거)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        goals = json.loads(content)
        return goals

    async def analyze_profile_and_set_goals(self, profile: dict) -> list[dict]:
        """
        Kafka 이벤트(User.ProfileUpdated)로 받은 프로필 처리 진입점
        """
        return await self.generate_goals(
            employee_id=profile.get("employee_id", ""),
            employee_name=profile.get("employee_name", ""),
            department=profile.get("department", ""),
            role=profile.get("role", ""),
            career_level=profile.get("career_level", "junior"),
            experience_years=profile.get("experience_years", 0),
            skills=profile.get("skills", []),
        )

    async def extract_profile_from_pdf_text(self, pdf_text: str) -> dict:
        """
        PDF에서 추출한 원문 텍스트를 LLM으로 분석하여 직원 프로필을 구조화합니다.
        Returns: {employee_name, department, role, career_level, experience_years, skills}
        """
        messages = [
            SystemMessage(content=PROFILE_EXTRACT_PROMPT),
            HumanMessage(content=f"다음 텍스트에서 직원 정보를 추출해주세요:\n\n{pdf_text[:4000]}"),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        profile = json.loads(content)
        logger.info(f"[ProfileExtract] 추출 결과: name={profile.get('employee_name')}, "
                    f"dept={profile.get('department')}, role={profile.get('role')}, "
                    f"skills={profile.get('skills', [])}")
        return profile


goal_setter_agent = GoalSetterAgent()
