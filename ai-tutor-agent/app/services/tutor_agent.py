"""
AI Tutor Agent (RAG 기반)
- 실시간 AI 튜터링 (대화)
- 퀴즈/과제 자동 채점 및 피드백
- 성장 리포트 생성
- 학습 이상 징후 탐지
"""
import json
import logging
import random
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from app.config import settings
from app.rag.qdrant_client import search_relevant_content

logger = logging.getLogger(__name__)

TUTOR_SYSTEM_PROMPT = """당신은 신입사원 교육을 담당하는 친절하고 전문적인 AI 튜터입니다.
학습자의 질문에 명확하고 이해하기 쉽게 답변하며, 실무 예제를 적극 활용합니다.

답변 원칙:
1. 학습자 수준에 맞게 설명 (초보자 친화적)
2. 구체적인 예시와 코드 제공
3. 추가 학습 자료 안내
4. 이해 확인 질문으로 마무리
5. 격려와 긍정적 피드백 제공

참고 자료가 제공될 경우 반드시 이를 활용하여 답변하세요."""

GRADING_SYSTEM_PROMPT = """당신은 공정하고 상세한 피드백을 제공하는 교육 평가 AI입니다.
학생의 답변을 채점하고 구체적인 개선 방향을 제시합니다.

반드시 아래 JSON 형식으로 응답하세요:
{{
  "score": 점수(0~100),
  "passed": true/false,
  "summary": "전체 평가 요약",
  "strengths": ["잘한 점1", "잘한 점2"],
  "weaknesses": ["부족한 점1", "부족한 점2"],
  "recommendations": ["개선 방향1", "개선 방향2"],
  "detail": "상세 피드백 (마크다운)"
}}"""

REPORT_SYSTEM_PROMPT = """당신은 학습 분석 전문 AI입니다.
학습자의 활동 데이터를 분석하여 성장 리포트를 생성합니다.

반드시 아래 JSON 형식으로 응답하세요:
{{
  "strengths": ["강점1", "강점2"],
  "weaknesses": ["개선점1", "개선점2"],
  "growth_trend": "improving|stable|declining",
  "recommendations": ["권장사항1", "권장사항2"],
  "report_content": "마크다운 형식의 상세 리포트"
}}"""


class AITutorAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.7,
        )
        self.grading_llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.3,  # 채점은 일관성 중요
        )

    async def chat(
        self,
        user_message: str,
        conversation_history: list[dict],
        module_title: str | None = None,
        rag_context: list[str] | None = None,
    ) -> tuple[str, list[str]]:
        """
        RAG 기반 실시간 AI 튜터링
        Returns: (answer, rag_sources) — rag_sources는 참고 자료 텍스트 목록
        """
        # RAG: 외부에서 전달되지 않은 경우에만 검색
        if rag_context is None:
            rag_query = f"{module_title or ''} {user_message}"
            try:
                rag_context = await search_relevant_content(rag_query, k=3)
            except Exception as e:
                logger.warning(f"[RAG] 검색 실패: {e}")
                rag_context = []

        rag_text = "\n\n".join(rag_context) if rag_context else ""

        system_content = TUTOR_SYSTEM_PROMPT
        if module_title:
            system_content += f"\n\n현재 학습 모듈: {module_title}"
        if rag_text:
            system_content += f"\n\n[참고 자료]\n{rag_text[:2000]}"

        messages = [SystemMessage(content=system_content)]

        # 대화 히스토리 추가 (최근 10개만)
        for msg in conversation_history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=user_message))

        response = await self.llm.ainvoke(messages)
        return response.content, rag_context

    async def grade_quiz(
        self,
        question: str,
        answer: str,
        student_answer: str,
        max_score: float = 100.0,
    ) -> dict:
        """퀴즈 자동 채점"""
        user_message = f"""다음 퀴즈를 채점해주세요:

[문제]
{question}

[모범 답안]
{answer}

[학생 답안]
{student_answer}

[배점] {max_score}점

채점 결과를 JSON 형식으로 반환해주세요."""

        messages = [
            SystemMessage(content=GRADING_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.grading_llm.ainvoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        result["score"] = min(float(result.get("score", 0)), max_score)
        result["max_score"] = max_score
        return result

    async def grade_assignment(
        self,
        assignment_title: str,
        assignment_description: str,
        student_submission: str,
        rubric: str | None = None,
        max_score: float = 100.0,
    ) -> dict:
        """과제 자동 채점"""
        rubric_section = f"\n[채점 기준(루브릭)]\n{rubric}" if rubric else ""
        user_message = f"""다음 과제를 채점해주세요:

[과제명]
{assignment_title}

[과제 설명]
{assignment_description}{rubric_section}

[학생 제출물]
{student_submission}

[총 배점] {max_score}점

채점 결과를 JSON 형식으로 반환해주세요."""

        messages = [
            SystemMessage(content=GRADING_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.grading_llm.ainvoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        result = json.loads(content)
        result["score"] = min(float(result.get("score", 0)), max_score)
        result["max_score"] = max_score
        return result

    async def generate_quiz(
        self,
        module_title: str,
        learning_objectives: list[str],
        content: str = "",
        num_questions: int = 4,
    ) -> list[dict]:
        """모듈 학습 목표 기반 객관식 퀴즈 생성"""
        objectives_text = "\n".join([f"- {o}" for o in learning_objectives]) or "없음"
        content_snippet = content[:1500] if content else ""

        user_message = f"""다음 학습 모듈에 대한 퀴즈를 {num_questions}문제 만들어주세요.

[모듈명]
{module_title}

[학습 목표]
{objectives_text}

[학습 내용 요약]
{content_snippet}

반드시 아래 JSON 배열 형식으로만 응답하세요 (다른 텍스트 없이):
[
  {{
    "id": 1,
    "question": "문제 내용",
    "options": ["A. 보기1", "B. 보기2", "C. 보기3", "D. 보기4"],
    "correct_answer": "B",
    "explanation": "정답 해설",
    "points": 25
  }},
  {{
    "id": 2,
    "question": "문제 내용",
    "options": ["A. 보기1", "B. 보기2", "C. 보기3", "D. 보기4"],
    "correct_answer": "D",
    "explanation": "정답 해설",
    "points": 25
  }}
]

규칙:
- 객관식 4지 선다 (A/B/C/D)
- correct_answer는 반드시 "A", "B", "C", "D" 중 하나
- **정답이 특정 보기에 편중되지 않도록 A, B, C, D를 고르게 분배하세요. 모든 문제의 정답이 같은 보기여서는 안 됩니다.**
- 학습 목표를 직접 검증하는 문제
- {num_questions}문제, 총 합계 100점 (각 {100 // num_questions}점)
"""

        messages = [
            SystemMessage(content="당신은 교육 퀴즈를 만드는 전문가입니다. 반드시 JSON 배열만 반환하세요."),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        content_str = response.content.strip()
        if "```json" in content_str:
            content_str = content_str.split("```json")[1].split("```")[0].strip()
        elif "```" in content_str:
            content_str = content_str.split("```")[1].split("```")[0].strip()

        questions = json.loads(content_str)
        if not isinstance(questions, list):
            return []

        labels = ["A", "B", "C", "D"]
        for q in questions:
            options = q.get("options", [])
            correct = str(q.get("correct_answer", "A")).strip().upper()

            # 현재 정답 텍스트 추출 (예: "A. 내용" → "내용")
            correct_idx = labels.index(correct) if correct in labels else 0
            if correct_idx < len(options):
                correct_text = options[correct_idx]
            else:
                correct_text = options[0] if options else ""

            # 보기 순서를 무작위로 섞고 레이블(A/B/C/D) 재부여
            shuffled = options[:]
            random.shuffle(shuffled)
            relabeled = []
            new_correct = correct
            for i, opt in enumerate(shuffled):
                # 기존 레이블 제거 후 새 레이블 붙이기 (예: "B. 내용" → "A. 내용")
                text = opt[3:] if len(opt) > 2 and opt[1] == '.' else opt
                relabeled.append(f"{labels[i]}. {text.lstrip()}")
                if opt == correct_text:
                    new_correct = labels[i]

            q["options"] = relabeled
            q["correct_answer"] = new_correct

        return questions

    async def grade_quiz_batch(
        self,
        questions: list[dict],
        student_answers: list[str],
        user_id: str = "0",
        module_id: str | None = None,
    ) -> dict:
        """여러 퀴즈 문항 일괄 채점 (객관식 자동 채점 + 해설)"""
        total = 0.0
        max_total = 0.0
        per_question = []

        for i, q in enumerate(questions):
            correct = str(q.get("correct_answer", "")).strip().upper()
            student = str(student_answers[i] if i < len(student_answers) else "").strip().upper()
            points = float(q.get("points", 25))
            max_total += points

            is_correct = correct == student
            earned = points if is_correct else 0.0
            total += earned

            per_question.append({
                "id": q.get("id", i + 1),
                "question": q.get("question", ""),
                "correct_answer": correct,
                "student_answer": student,
                "is_correct": is_correct,
                "earned": earned,
                "points": points,
                "explanation": q.get("explanation", ""),
            })

        passed = (total / max_total) >= 0.6 if max_total > 0 else False
        return {
            "total_score": total,
            "max_score": max_total,
            "passed": passed,
            "per_question": per_question,
            "summary": f"{int(total)}/{int(max_total)}점 — {'합격' if passed else '재도전 권장'}",
        }

    async def generate_growth_report(
        self,
        employee_name: str,
        period_days: int,
        total_sessions: int,
        total_learning_hours: float,
        average_score: float,
        recent_activities: list[dict],
        recent_feedback: list[dict],
    ) -> dict:
        """성장 리포트 생성"""
        activities_summary = "\n".join([
            f"- [{a.get('activity_type')}] 모듈: {a.get('module_id', 'N/A')}, "
            f"점수: {a.get('score', 'N/A')}, 시간: {a.get('duration_minutes', 0)}분"
            for a in recent_activities[-20:]
        ])

        feedback_summary = "\n".join([
            f"- 유형: {f.get('feedback_type')}, 점수: {f.get('score', 'N/A')}, "
            f"통과: {f.get('passed', 'N/A')}"
            for f in recent_feedback[-10:]
        ])

        user_message = f"""다음 학습자의 성장 리포트를 작성해주세요:

[학습자 정보]
이름: {employee_name}
분석 기간: 최근 {period_days}일

[학습 통계]
- 총 세션 수: {total_sessions}회
- 총 학습 시간: {total_learning_hours:.1f}시간
- 평균 점수: {average_score:.1f}점

[최근 활동]
{activities_summary if activities_summary else '데이터 없음'}

[최근 평가 결과]
{feedback_summary if feedback_summary else '데이터 없음'}

위 데이터를 분석하여 성장 리포트를 JSON 형식으로 작성해주세요."""

        messages = [
            SystemMessage(content=REPORT_SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        response = await self.llm.ainvoke(messages)
        content = response.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)

    def detect_anomaly(
        self,
        employee_id: str,
        last_activity_at: datetime | None,
        recent_scores: list[float],
        consecutive_fails: int,
    ) -> dict | None:
        """
        학습 이상 징후 탐지
        Returns: anomaly dict or None
        """
        now = datetime.utcnow()

        # 1. 장기 비활성
        if last_activity_at:
            hours_inactive = (now - last_activity_at).total_seconds() / 3600
            if hours_inactive >= settings.ANOMALY_INACTIVITY_HOURS:
                return {
                    "anomaly_type": "inactivity",
                    "description": f"{int(hours_inactive)}시간 동안 학습 활동 없음",
                    "severity": "high" if hours_inactive >= 72 else "medium",
                }

        # 2. 연속 실패
        if consecutive_fails >= settings.ANOMALY_CONSECUTIVE_FAILS:
            return {
                "anomaly_type": "consecutive_fail",
                "description": f"{consecutive_fails}회 연속 평가 실패",
                "severity": "high",
            }

        # 3. 낮은 점수 패턴
        if recent_scores and len(recent_scores) >= 3:
            avg = sum(recent_scores) / len(recent_scores)
            if avg <= settings.ANOMALY_LOW_SCORE_THRESHOLD:
                return {
                    "anomaly_type": "low_score",
                    "description": f"최근 평균 점수 {avg:.1f}점 (기준: {settings.ANOMALY_LOW_SCORE_THRESHOLD}점)",
                    "severity": "medium",
                }

        return None


ai_tutor_agent = AITutorAgent()
