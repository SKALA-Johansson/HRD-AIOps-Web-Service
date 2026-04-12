import io
import json
import logging
import re
from datetime import datetime
from typing import Any, Optional
import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from pypdf import PdfReader
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.curriculum import Curriculum, Module
from app.models.standard_curriculum import StandardCurriculum
from app.schemas.curriculum import (
    CurriculumGenerateRequest,
    CurriculumUpdateRequest,
    CurriculumApproveRequest,
    CurriculumGeneratingResponse,
    CurriculumDetailResponse,
    SkillAnalysis,
    SkillDecision,
    ModuleSummary,
    ModuleResponse,
    CurriculumResponse,
)
from app.schemas.response import ApiResponse
from app.services.curriculum_agent import curriculum_designer_agent
from app.services.kafka_service import publish_event
from app.rag.qdrant_client import add_documents

logger = logging.getLogger(__name__)


async def _register_employee(employee_no: str, birth_date6: str, name: str, department: str) -> bool:
    """사원번호(username) + 생년월일(password)로 auth-server에 사원 계정을 자동 생성합니다."""
    if not employee_no or not birth_date6:
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{settings.AUTH_SERVER_URL}/api/v1/auth/signup",
                json={
                    "username": employee_no,
                    "password": birth_date6,
                    "name": name or employee_no,
                    "role": "EMPLOYEE",
                },
            )
        if res.status_code in (200, 201):
            logger.info(f"[Auth] 사원 자동 회원가입 성공: {employee_no}")
            return True
        elif res.status_code in (409, 500) and "already exists" in res.text.lower():
            logger.info(f"[Auth] 이미 존재하는 사원: {employee_no}")
            return True
        else:
            logger.warning(f"[Auth] 회원가입 실패 {res.status_code}: {res.text[:200]}")
            return False
    except Exception as e:
        logger.warning(f"[Auth] 회원가입 요청 오류: {e}")
        return False

_PROFILE_EXTRACT_PROMPT = """PDF 텍스트에서 직원 정보를 추출해 반드시 JSON으로 반환하세요.
{
  "employee_name": "이름 (없으면 '신입사원')",
  "department": "부서 (없으면 '미분류')",
  "role": "직무 (없으면 '신입')",
  "career_level": "junior|mid|senior",
  "experience_years": 0,
  "skills": ["스킬1", "스킬2"]
}"""


async def _extract_profile_from_pdf_text(pdf_text: str) -> dict:
    """PDF 원문 → LLM → 직원 프로필 dict"""
    llm = ChatOpenAI(model=settings.OPENAI_MODEL, api_key=settings.OPENAI_API_KEY, temperature=0)
    messages = [
        SystemMessage(content=_PROFILE_EXTRACT_PROMPT),
        HumanMessage(content=f"다음 텍스트에서 직원 정보를 추출하세요:\n\n{pdf_text[:4000]}"),
    ]
    response = await llm.ainvoke(messages)
    content = response.content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(content)
    except Exception:
        return {}

router = APIRouter(prefix="/curriculums", tags=["curriculums"])


# ── 내부 헬퍼 ──────────────────────────────────────────────────────

def _normalize_text(value: str) -> str:
    return re.sub(r"[^0-9a-zA-Z가-힣]+", "", (value or "").lower())


def _tokenize_text(value: str) -> set[str]:
    cleaned = re.sub(r"[^0-9a-zA-Z가-힣]+", " ", (value or "").lower()).strip()
    base = {t for t in cleaned.split() if len(t) >= 2 or t in {"ai", "ml", "llm", "db"}}

    # 부서명 표현 차이를 줄이기 위한 동의어 토큰 보강
    if "backend" in cleaned or "백엔드" in cleaned:
        base.update({"백엔드", "개발"})
    if "frontend" in cleaned or "프론트" in cleaned:
        base.update({"프론트엔드", "개발"})
    if "ai" in cleaned or "데이터" in cleaned:
        base.update({"ai", "데이터"})
    if "sales" in cleaned or "영업" in cleaned:
        base.update({"영업"})
    return base


def _normalize_skills(skills: list[str] | None) -> list[str]:
    if not skills:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw in skills:
        if raw is None:
            continue
        parts = [p.strip() for p in re.split(r"[,/\n;|]+", str(raw)) if p.strip()]
        for part in parts:
            key = _normalize_text(part)
            if not key or key in seen:
                continue
            seen.add(key)
            normalized.append(part)
    return normalized


def _skill_matches_topic(skill: str, topic: str) -> bool:
    s = _normalize_text(skill)
    t = _normalize_text(topic)
    if not s or not t:
        return False
    return s in t or t in s


def _filter_modules_by_existing_skills(standard_modules: list[dict], existing_skills: list[str]) -> list[dict]:
    """
    이미 보유한 역량과 모듈 topic이 전부 겹치는 모듈은 제거합니다.
    부분 겹침 모듈은 겹치는 topic만 제거해 남깁니다.
    """
    skills = _normalize_skills(existing_skills)
    if not skills:
        return standard_modules

    filtered: list[dict] = []
    for module in standard_modules:
        topics = [str(t).strip() for t in module.get("topics", []) if str(t).strip()]
        if not topics:
            filtered.append(module)
            continue

        covered = [t for t in topics if any(_skill_matches_topic(skill, t) for skill in skills)]
        remaining = [t for t in topics if t not in covered]

        # 모듈의 핵심 topics가 모두 보유 역량이면 해당 모듈은 제외
        if covered and not remaining:
            logger.info(f"[Personalize] 모듈 제외: {module.get('title')} / covered_topics={covered}")
            continue

        if covered and remaining:
            updated = dict(module)
            updated["topics"] = remaining
            desc = (updated.get("description") or "").strip()
            covered_text = ", ".join(covered[:3])
            note = f"보유 역량 제외: {covered_text}"
            updated["description"] = f"{desc} ({note})" if desc else note
            filtered.append(updated)
            logger.info(f"[Personalize] 모듈 조정: {module.get('title')} / removed_topics={covered}")
            continue

        filtered.append(module)

    # 전부 제외되는 경우에도 빈 결과를 유지 (역량 기반 제외를 우선)
    return filtered


def _extract_uploaded_contents(payload: Any) -> list[dict]:
    """
    content-service 응답(JSON)에서 교육 콘텐츠 목록만 추출합니다.
    예상 형식:
      {"status":"SUCCESS","message":"...","data":[{title,category,fileUrl,tags}, ...]}
    """
    if not isinstance(payload, dict):
        return []

    raw_data = payload.get("data")
    if not isinstance(raw_data, list):
        return []

    items: list[dict] = []
    seen_titles: set[str] = set()
    for raw in raw_data:
        if not isinstance(raw, dict):
            continue
        title = str(raw.get("title") or "").strip()
        if not title:
            continue

        key = _normalize_text(title)
        if key and key in seen_titles:
            continue
        if key:
            seen_titles.add(key)

        tags_raw = raw.get("tags")
        tags = []
        if isinstance(tags_raw, list):
            tags = [str(t).strip() for t in tags_raw if str(t).strip()]

        items.append(
            {
                "title": title,
                "category": str(raw.get("category") or "").strip(),
                "file_url": str(raw.get("fileUrl") or raw.get("file_url") or "").strip(),
                "tags": tags,
            }
        )
    return items


async def _fetch_uploaded_contents() -> list[dict]:
    """현재 등록된 교육 콘텐츠 목록을 content-service에서 조회합니다."""
    endpoint = f"{settings.CONTENT_SERVICE_URL}/api/v1/contents"
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.get(endpoint)
        if response.status_code != 200:
            logger.warning(f"[Content] 목록 조회 실패: status={response.status_code}")
            return []
        try:
            body = response.json()
        except Exception:
            logger.warning("[Content] 목록 조회 응답 JSON 파싱 실패")
            return []
        contents = _extract_uploaded_contents(body)
        logger.info(f"[Content] 등록 콘텐츠 {len(contents)}건 조회")
        return contents
    except Exception as e:
        logger.warning(f"[Content] 목록 조회 오류: {e}")
        return []


def _content_tokens(content: dict) -> set[str]:
    values: list[str] = [str(content.get("title") or ""), str(content.get("category") or "")]
    tags = content.get("tags") or []
    values.extend([str(t) for t in tags])

    tokens: set[str] = set()
    for value in values:
        tokens.update(_tokenize_text(value))
        norm = _normalize_text(value)
        if norm:
            tokens.add(norm)
    return tokens


def _match_contents_for_module(module: dict, uploaded_contents: list[dict], limit: int = 3) -> list[dict]:
    """
    모듈 제목/설명/topics와 현재 등록 콘텐츠의 제목/카테고리/tags를 매칭해
    관련성 높은 콘텐츠 후보를 반환합니다.
    """
    if not uploaded_contents:
        return []

    module_terms: list[str] = [str(module.get("title") or ""), str(module.get("description") or "")]
    topics = [str(t).strip() for t in module.get("topics", []) if str(t).strip()]
    module_terms.extend(topics)

    module_tokens: set[str] = set()
    for term in module_terms:
        module_tokens.update(_tokenize_text(term))
        norm = _normalize_text(term)
        if norm:
            module_tokens.add(norm)

    if not module_tokens:
        return []

    scored: list[tuple[int, dict]] = []
    for content in uploaded_contents:
        c_tokens = _content_tokens(content)
        if not c_tokens:
            continue

        overlap = len(module_tokens & c_tokens)
        if overlap <= 0:
            continue

        title_norm = _normalize_text(str(content.get("title") or ""))
        strong_match = any(t and (t in title_norm or title_norm in t) for t in module_tokens if len(t) >= 2)
        score = overlap * 10 + (20 if strong_match else 0)
        scored.append((score, content))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [content for _, content in scored[:limit]]


def _filter_modules_by_uploaded_contents(
    standard_modules: list[dict],
    uploaded_contents: list[dict],
) -> tuple[list[dict], dict[str, list[dict]]]:
    """
    등록된 콘텐츠와 매칭되는 모듈만 남겨 커리큘럼 후보를 구성합니다.
    반환:
      - 필터링된 모듈 목록
      - 모듈 제목별 추천 콘텐츠 맵
    """
    if not uploaded_contents:
        return standard_modules, {}

    filtered: list[dict] = []
    module_content_map: dict[str, list[dict]] = {}

    for module in standard_modules:
        matched = _match_contents_for_module(module, uploaded_contents, limit=3)
        if not matched:
            logger.info(f"[Personalize] 모듈 제외(콘텐츠 미매칭): {module.get('title')}")
            continue

        updated = dict(module)
        desc = (updated.get("description") or "").strip()
        match_titles = ", ".join([m.get("title", "") for m in matched[:2] if m.get("title")])
        if match_titles:
            note = f"추천 콘텐츠: {match_titles}"
            updated["description"] = f"{desc} ({note})" if desc else note

        filtered.append(updated)
        module_title = str(updated.get("title") or "").strip()
        if module_title:
            module_content_map[module_title] = matched

    if filtered:
        return filtered, module_content_map

    # 콘텐츠가 있으나 전부 미매칭이면 빈 결과를 반환 (fail-safe)
    logger.warning("[Personalize] 콘텐츠 매칭 결과 없음: 표준 모듈 전체 제외")
    return [], {}


def _content_to_resource_text(content: dict) -> str:
    title = str(content.get("title") or "").strip()
    url = str(content.get("file_url") or content.get("fileUrl") or "").strip()
    return f"{title} ({url})" if title and url else title


def _content_key(content: dict) -> str:
    return _normalize_text(str(content.get("title") or ""))


def _content_terms(content: dict) -> list[str]:
    terms = [
        str(content.get("title") or "").strip(),
        str(content.get("category") or "").strip(),
    ]
    tags = content.get("tags") or []
    terms.extend([str(t).strip() for t in tags if str(t).strip()])
    return [t for t in terms if t]


def _is_content_covered_by_existing_skills(content: dict, existing_skills: list[str]) -> bool:
    """
    교육 콘텐츠 주제가 사원 보유 역량과 충분히 겹치면 True.
    - 역량 기반 포함/제외 판단의 fail-safe 용도로 사용.
    """
    skills = _normalize_skills(existing_skills)
    if not skills:
        return False
    terms = _content_terms(content)
    return any(_skill_matches_topic(skill, term) for skill in skills for term in terms)


def _select_eligible_contents(uploaded_contents: list[dict], existing_skills: list[str]) -> list[dict]:
    eligible = [c for c in uploaded_contents if not _is_content_covered_by_existing_skills(c, existing_skills)]
    if eligible:
        return eligible
    # 전부 보유 역량으로 판정되더라도 학습 공백 방지를 위해 원본 유지 (단, 존재 콘텐츠만 사용)
    logger.info("[Personalize] 모든 콘텐츠가 보유 역량으로 판정되어 원본 콘텐츠 목록을 유지합니다.")
    return uploaded_contents


def _default_module_title_from_content(content: dict) -> str:
    raw = str(content.get("title") or "").strip()
    title = re.sub(r"\.(pdf|pptx|ppt|docx|doc|xlsx|xls)$", "", raw, flags=re.IGNORECASE).strip()
    return title or "등록 콘텐츠 기반 학습"


def _sanitize_to_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        s = str(item).strip()
        if s:
            result.append(s)
    return result


def _safe_int(value: Any, default: int = 8) -> int:
    try:
        return int(value)
    except Exception:
        matched = re.search(r"\d+", str(value or ""))
        return int(matched.group()) if matched else default


def _strictly_align_generated_modules(
    generated_modules: list[dict],
    uploaded_contents: list[dict],
    existing_skills: list[str],
    excluded_content_titles: set[str] | None = None,
) -> list[dict]:
    """
    LLM 결과를 '등록된 교육 콘텐츠' 기준으로 강제 정합합니다.
    규칙:
    - 모듈당 1개 실존 콘텐츠만 연결
    - 동일 콘텐츠 중복 사용 금지
    - EXCLUDE 판정 콘텐츠는 fallback에서도 추가 금지
    - 매칭 실패 모듈 제외
    - 마지막에 주차 번호 재할당
    """
    excluded_keys: set[str] = {
        _normalize_text(t) for t in (excluded_content_titles or []) if t
    }

    eligible_contents = _select_eligible_contents(uploaded_contents, existing_skills)
    if not eligible_contents:
        return []

    used_content_keys: set[str] = set()
    aligned: list[dict] = []

    for mod in generated_modules or []:
        if not isinstance(mod, dict):
            continue
        probe_module = {
            "title": mod.get("title", ""),
            "description": mod.get("description", ""),
            "topics": _sanitize_to_list(mod.get("learning_objectives", [])),
        }
        matches = _match_contents_for_module(probe_module, eligible_contents, limit=len(eligible_contents))
        picked: Optional[dict] = None
        for match in matches:
            key = _content_key(match)
            if key and key not in used_content_keys and key not in excluded_keys:
                picked = match
                used_content_keys.add(key)
                break

        if not picked:
            continue

        module_title = str(mod.get("title") or "").strip() or _default_module_title_from_content(picked)
        aligned.append(
            {
                "week_number": len(aligned) + 1,
                "title": module_title,
                "description": str(mod.get("description") or "").strip(),
                "content": str(mod.get("content") or "").strip(),
                "learning_objectives": _sanitize_to_list(mod.get("learning_objectives", [])),
                "assignments": _sanitize_to_list(mod.get("assignments", [])),
                "estimated_hours": _safe_int(mod.get("estimated_hours", 8), default=8),
                "resources": [_content_to_resource_text(picked)],
            }
        )

    # LLM이 일부 콘텐츠를 modules에 누락한 경우: EXCLUDE 판정이 아닌 콘텐츠만 보완
    for content in eligible_contents:
        key = _content_key(content)
        if not key or key in used_content_keys or key in excluded_keys:
            continue
        title = _default_module_title_from_content(content)
        aligned.append(
            {
                "week_number": len(aligned) + 1,
                "title": title,
                "description": "현재 등록된 교육 콘텐츠 기반 학습 모듈",
                "content": "",
                "learning_objectives": [f"{title} 학습 내용 이해 및 실무 적용"],
                "assignments": [],
                "estimated_hours": 8,
                "resources": [_content_to_resource_text(content)],
            }
        )
        used_content_keys.add(key)

    return aligned


def _align_modules_from_standard(
    generated_modules: list[dict],
    uploaded_contents: list[dict],
) -> list[dict]:
    """
    표준 커리큘럼 기반 생성 결과 정합.
    - LLM이 INCLUDE/ADVANCED로 포함한 모듈을 그대로 사용
    - 업로드된 교육 콘텐츠는 리소스로만 첨부 (모듈 게이팅 없음)
    - 주차 번호 1부터 재할당
    """
    aligned: list[dict] = []
    for mod in generated_modules or []:
        if not isinstance(mod, dict):
            continue

        title = str(mod.get("title") or "").strip()
        if not title:
            continue

        # 업로드 콘텐츠에서 관련 리소스 탐색 (첨부만, 배제 기준 아님)
        probe = {
            "title": title,
            "description": str(mod.get("description") or ""),
            "topics": _sanitize_to_list(mod.get("learning_objectives", [])),
        }
        matched = _match_contents_for_module(probe, uploaded_contents, limit=2) if uploaded_contents else []

        resources = _sanitize_to_list(mod.get("resources", []))
        for content in matched:
            resource_text = _content_to_resource_text(content)
            if resource_text and resource_text not in resources:
                resources.append(resource_text)

        aligned.append(
            {
                "week_number": len(aligned) + 1,
                "title": title,
                "description": str(mod.get("description") or "").strip(),
                "content": str(mod.get("content") or "").strip(),
                "learning_objectives": _sanitize_to_list(mod.get("learning_objectives", [])),
                "assignments": _sanitize_to_list(mod.get("assignments", [])),
                "estimated_hours": _safe_int(mod.get("estimated_hours", 8), default=8),
                "resources": resources,
            }
        )

    return aligned


def _select_standard_curriculum(
    db: Session,
    department: str,
    role: str,
    career_level: str,
) -> Optional[StandardCurriculum]:
    candidates = db.query(StandardCurriculum).filter(StandardCurriculum.is_active == True).all()
    if not candidates:
        return None

    dept_norm = _normalize_text(department)
    role_norm = _normalize_text(role)
    dept_tokens = _tokenize_text(department)
    role_tokens = _tokenize_text(role)

    best_score = -1
    best: Optional[StandardCurriculum] = None

    for sc in candidates:
        score = 0
        sc_dept_norm = _normalize_text(sc.department)
        sc_role_norm = _normalize_text(sc.role)
        sc_dept_tokens = _tokenize_text(sc.department)
        sc_role_tokens = _tokenize_text(sc.role)

        if dept_norm and (dept_norm == sc_dept_norm or dept_norm in sc_dept_norm or sc_dept_norm in dept_norm):
            score += 90
        score += len(dept_tokens & sc_dept_tokens) * 25

        if role_norm and (role_norm == sc_role_norm or role_norm in sc_role_norm or sc_role_norm in role_norm):
            score += 40
        score += len(role_tokens & sc_role_tokens) * 15

        if career_level and sc.career_level == (career_level or "junior"):
            score += 10

        if score > best_score:
            best_score = score
            best = sc

    return best

def _to_detail(c: Curriculum) -> CurriculumDetailResponse:
    """api.md §9 응답 형식"""
    # 역량 분석 결과 변환
    skill_analysis = None
    raw_analysis = c.get_skill_analysis()
    if raw_analysis:
        decisions = [
            SkillDecision(
                module_title=d.get("module_title", ""),
                action=d.get("action", "INCLUDE"),
                reason=d.get("reason", ""),
            )
            for d in raw_analysis.get("decisions", [])
            if isinstance(d, dict)
        ]
        skill_analysis = SkillAnalysis(
            detected_skills=raw_analysis.get("detected_skills", []),
            decisions=decisions,
        )

    return CurriculumDetailResponse(
        curriculumId=c.id,
        goalId=c.goal_id,
        employeeName=c.employee_name or None,
        employeeId=c.employee_id or None,
        department=c.department or None,
        title=c.title,
        status=c.status.upper(),
        modules=[
            ModuleSummary(moduleId=m.id, week=m.week_number, title=m.title)
            for m in sorted(c.modules, key=lambda x: x.week_number)
        ],
        existingSkills=c.get_existing_skills(),
        skillAnalysis=skill_analysis,
    )


def _module_to_response(m: Module) -> ModuleResponse:
    return ModuleResponse(
        id=m.id,
        curriculum_id=m.curriculum_id,
        week_number=m.week_number,
        title=m.title,
        description=m.description,
        content=m.content,
        learning_objectives=m.get_learning_objectives(),
        resources=m.get_resources(),
        assignments=m.get_assignments(),
        estimated_hours=m.estimated_hours,
        created_at=m.created_at,
    )


async def _run_curriculum_generation(curriculum_id: str, goal_id: str, existing_skills: list[str], pdf_text: str = ""):
    """
    백그라운드 태스크: 정석 커리큘럼 기반 맞춤형 커리큘럼 자동 생성
    1. PDF 텍스트에서 LLM으로 역량/스킬 추출 (pdf_text 있으면)
    2. 부서/역할에 맞는 정석 커리큘럼 조회
    3. 직원 기보유 스킬로 불필요 모듈 제거 후 LLM 개인화
    4. 정석 커리큘럼 없으면 자유 생성으로 폴백
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
        if not curriculum:
            return

        # PDF 텍스트가 있으면 LLM으로 역량 추출 (백그라운드에서 처리)
        if pdf_text.strip() and not existing_skills:
            try:
                profile = await _extract_profile_from_pdf_text(pdf_text)
                existing_skills = _normalize_skills(profile.get("skills", []))
                # PDF에서 추출한 역할/레벨 정보로 커리큘럼 업데이트
                if profile.get("role"):
                    curriculum.role = profile["role"]
                if profile.get("career_level"):
                    curriculum.career_level = profile["career_level"]
                db.commit()
                logger.info(f"[PDF] 역량 추출 완료: {existing_skills}")
            except Exception as e:
                logger.warning(f"[PDF] 역량 추출 실패 (기본값 사용): {e}")
        else:
            existing_skills = _normalize_skills(existing_skills)

        mock_goals = [{
            "title": "핵심 역량 강화",
            "description": "직무 필수 역량 개발",
            "priority": "high",
            "duration_weeks": 12,
            "skills_to_learn": [],
            "success_criteria": "실무 적용 가능 수준 도달",
        }]
        uploaded_contents = await _fetch_uploaded_contents()

        standard = _select_standard_curriculum(
            db=db,
            department=curriculum.department or "",
            role=curriculum.role or "",
            career_level=curriculum.career_level or "junior",
        )
        logger.info(
            f"[Standard] 입력 dept='{curriculum.department}', role='{curriculum.role}', "
            f"selected='{(standard.department + '/' + standard.role) if standard else '없음 → 자유 생성'}'"
        )

        if standard and standard.modules:
            # 표준 커리큘럼 기반 맞춤 생성
            # 1) 표준 모듈 전체 로드
            standard_modules = [
                {
                    "week_number": m.week_number,
                    "title": m.title,
                    "description": m.description,
                    "topics": m.get_topics(),
                    "learning_objectives": m.get_learning_objectives(),
                    "estimated_hours": m.estimated_hours,
                }
                for m in standard.modules
            ]

            # 2) 코드 레벨 사전 필터: 보유 역량과 완전히 겹치는 모듈 제거
            if existing_skills:
                before_count = len(standard_modules)
                standard_modules = _filter_modules_by_existing_skills(standard_modules, existing_skills)
                logger.info(
                    f"[Personalize] 사전 필터: {before_count}개 → {len(standard_modules)}개 "
                    f"({before_count - len(standard_modules)}개 보유 역량으로 제외)"
                )

            if not standard_modules:
                # 모든 모듈이 보유 역량으로 제외된 경우 (거의 없지만 방어)
                curriculum.title = curriculum.title or f"{curriculum.department} 맞춤 커리큘럼"
                curriculum.description = "보유 역량 분석 결과 모든 표준 모듈을 이미 습득한 것으로 판단되어 추가 모듈이 없습니다."
                curriculum.total_weeks = 0
                curriculum.status = "draft"
                db.commit()
                await publish_event("Curriculum.Created", {
                    "curriculum_id": curriculum.id,
                    "goal_id": goal_id,
                    "employee_id": curriculum.employee_id,
                    "title": curriculum.title,
                })
                logger.info(f"[Curriculum] 모든 표준 모듈 보유 역량 제외: curriculum_id={curriculum.id}")
                return

            # 3) LLM으로 2차 개인화 (INCLUDE/ADVANCED/EXCLUDE 판단)
            curriculum_data = await curriculum_designer_agent.design_personalized_curriculum(
                standard_modules=standard_modules,
                employee_name=curriculum.employee_name,
                department=curriculum.department,
                role=curriculum.role,
                career_level=curriculum.career_level,
                existing_skills=existing_skills,
                goals=mock_goals,
                content_catalog=uploaded_contents,
                module_content_map={},
            )

            skill_analysis_raw = curriculum_data.get("skill_analysis") or {}
            excluded_module_titles = {
                d.get("module_title", "")
                for d in skill_analysis_raw.get("decisions", [])
                if isinstance(d, dict) and d.get("action", "").upper() == "EXCLUDE"
            }
            logger.info(f"[Curriculum] LLM EXCLUDE 판정 표준 모듈: {excluded_module_titles}")

            # 4) 표준 기반 정합: 업로드 콘텐츠는 리소스로만 첨부 (모듈 게이팅 없음)
            aligned_modules = _align_modules_from_standard(
                generated_modules=curriculum_data.get("modules", []),
                uploaded_contents=uploaded_contents,
            )
        else:
            # 표준 커리큘럼 없음 → 업로드 콘텐츠 기반 자유 생성
            if not uploaded_contents:
                curriculum.title = curriculum.title or "등록 콘텐츠 기반 커리큘럼"
                curriculum.description = "현재 등록된 교육 콘텐츠가 없어 모듈을 생성하지 않았습니다."
                curriculum.total_weeks = 0
                curriculum.status = "draft"
                db.commit()
                await publish_event("Curriculum.Created", {
                    "curriculum_id": curriculum.id,
                    "goal_id": goal_id,
                    "employee_id": curriculum.employee_id,
                    "title": curriculum.title,
                })
                logger.warning(f"[Curriculum] 등록 콘텐츠 없음으로 빈 커리큘럼 생성: curriculum_id={curriculum.id}")
                return

            curriculum_data = await curriculum_designer_agent.design_curriculum(
                employee_name=curriculum.employee_name,
                department=curriculum.department,
                role=curriculum.role,
                career_level=curriculum.career_level,
                experience_years=0,
                skills=existing_skills,
                goals=mock_goals,
                content_catalog=uploaded_contents,
            )

            skill_analysis_raw = curriculum_data.get("skill_analysis") or {}
            excluded_content_titles = {
                d.get("module_title", "")
                for d in skill_analysis_raw.get("decisions", [])
                if isinstance(d, dict) and d.get("action", "").upper() == "EXCLUDE"
            }

            aligned_modules = _strictly_align_generated_modules(
                generated_modules=curriculum_data.get("modules", []),
                uploaded_contents=uploaded_contents,
                existing_skills=existing_skills,
                excluded_content_titles=excluded_content_titles,
            )
        curriculum.total_weeks = len(aligned_modules)
        curriculum.status = "draft"

        # 역량 분석 결과 저장
        skill_analysis = curriculum_data.get("skill_analysis")
        if skill_analysis and isinstance(skill_analysis, dict):
            curriculum.set_skill_analysis(skill_analysis)
            detected = skill_analysis.get("detected_skills", [])
            if detected:
                curriculum.set_existing_skills(detected)
        if not curriculum.existing_skills and existing_skills:
            curriculum.set_existing_skills(existing_skills)

        for mod_data in aligned_modules:
            module = Module(
                curriculum_id=curriculum.id,
                week_number=mod_data.get("week_number", 1),
                title=mod_data.get("title", ""),
                description=mod_data.get("description", ""),
                content=mod_data.get("content", ""),
                estimated_hours=mod_data.get("estimated_hours", 8),
            )
            module.set_learning_objectives(mod_data.get("learning_objectives", []))
            module.set_resources(mod_data.get("resources", []))
            module.set_assignments(mod_data.get("assignments", []))
            db.add(module)

        db.commit()

        await publish_event("Curriculum.Created", {
            "curriculum_id": curriculum.id,
            "goal_id": goal_id,
            "employee_id": curriculum.employee_id,
            "title": curriculum.title,
        })
    except Exception as e:
        logger.exception(f"[Curriculum] 생성 실패: curriculum_id={curriculum_id}, error={e}")
        curriculum = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
        if curriculum:
            curriculum.status = "error"
            db.commit()
    finally:
        db.close()


# ── 7-a) 커리큘럼 목록 조회 ──────────────────────────────────────────

@router.get("")
def list_curriculums(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """GET /curriculums — 전체 목록 (선택: status 필터)"""
    q = db.query(Curriculum)
    if status:
        q = q.filter(Curriculum.status == status.lower())
    cs = q.order_by(Curriculum.created_at.desc()).limit(200).all()
    return ApiResponse.ok(
        data=[_to_detail(c) for c in cs],
        code="CURRICULUM-200",
        message="커리큘럼 목록 조회 성공",
    )


# ── 7-b) PDF로 커리큘럼 생성 (HR용) ─────────────────────────────────

@router.post("/generate-from-pdf", status_code=status.HTTP_202_ACCEPTED)
async def generate_curriculum_from_pdf(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    file: UploadFile = File(..., description="사원 정보 PDF"),
    name: str = Form(default="", description="사원 이름"),
    employeeNo: str = Form(default="", description="사원 번호"),
    birthDate6: str = Form(default="", description="생년월일 6자리 (초기 비밀번호)"),
    department: str = Form(default="", description="부서"),
    title: str = Form(default="", description="커리큘럼 제목"),
):
    """
    PDF → 사원 자동 회원가입 → 개인화 커리큘럼 자동 생성 (비동기).
    - 사번(employeeNo) + 생년월일(birthDate6)로 사원 계정을 즉시 생성합니다.
    - LLM 역량 추출 및 커리큘럼 생성은 백그라운드에서 처리됩니다.
    - curriculumId를 즉시 반환합니다.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="빈 파일입니다.")

    # 1. PDF 텍스트 추출 (pypdf, 빠름)
    try:
        reader = PdfReader(io.BytesIO(content))
        full_text = "\n".join(
            page.extract_text() or "" for page in reader.pages if (page.extract_text() or "").strip()
        )
    except Exception as e:
        logger.error(f"[PDF] 파싱 실패: {e}")
        raise HTTPException(status_code=422, detail=f"PDF 파싱 실패: {e}")

    final_name = name.strip() or "신입사원"
    final_dept = department.strip() or "미분류"
    final_title = title.strip() or f"{final_name} 맞춤형 커리큘럼"
    employee_no = employeeNo.strip()

    # 2. 사원 자동 회원가입 (사번=username, 생년월일=password)
    if employee_no and birthDate6.strip():
        await _register_employee(employee_no, birthDate6.strip(), final_name, final_dept)

    logger.info(f"[PDF Ingest] name={final_name}, dept={final_dept}, employeeNo={employee_no}")

    # 3. Curriculum 레코드 즉시 생성 (status=generating) — LLM은 백그라운드에서
    curriculum = Curriculum(
        goal_id="0",
        employee_id=employee_no or "0",
        employee_name=final_name,
        department=final_dept,
        role="신입",
        career_level="junior",
        title=final_title,
        total_weeks=12,
        status="generating",
    )
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)

    # 4. 백그라운드: LLM 역량 추출 + 커리큘럼 생성
    background_tasks.add_task(
        _run_curriculum_generation,
        curriculum.id,
        "0",
        [],          # existing_skills — 백그라운드에서 PDF 텍스트로부터 추출
        full_text,   # pdf_text 전달
    )

    return ApiResponse.created(
        data=CurriculumGeneratingResponse(curriculumId=curriculum.id, status="GENERATING"),
        code="CURRICULUM-202",
        message="PDF 기반 커리큘럼 생성 요청이 접수되었습니다.",
    )


# ── 8) 커리큘럼 자동 생성 요청 ────────────────────────────────────────

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_curriculum(
    request: CurriculumGenerateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    api.md §8 - POST /curriculums/generate
    비동기로 커리큘럼 생성을 시작하고 즉시 GENERATING 상태를 반환합니다.
    """
    curriculum = Curriculum(
        goal_id=str(request.goalId),
        employee_id="0",
        employee_name=request.employee_name or "TBD",
        department=request.department or "TBD",
        role=request.role or "TBD",
        career_level=request.career_level or "junior",
        title="커리큘럼 생성 중...",
        total_weeks=12,
        status="generating",
    )
    db.add(curriculum)
    db.commit()
    db.refresh(curriculum)

    background_tasks.add_task(
        _run_curriculum_generation,
        curriculum.id,
        str(request.goalId),
        request.existing_skills,
    )

    return ApiResponse.created(
        data=CurriculumGeneratingResponse(
            curriculumId=curriculum.id,
            status="GENERATING",
        ),
        code="CURRICULUM-202",
        message="커리큘럼 생성 요청이 접수되었습니다.",
    )


# ── 9) 개인 커리큘럼 조회 ──────────────────────────────────────────────

@router.get("/{curriculum_id}")
def get_curriculum(curriculum_id: str, db: Session = Depends(get_db)):
    """api.md §9 - GET /curriculums/{curriculumId}"""
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return ApiResponse.ok(
        data=_to_detail(c),
        code="CURRICULUM-200",
        message="커리큘럼 조회 성공",
    )


# ── 10) 커리큘럼 수정 요청 ────────────────────────────────────────────

@router.put("/{curriculum_id}")
async def update_curriculum(curriculum_id: str, request: CurriculumUpdateRequest, db: Session = Depends(get_db)):
    """
    api.md §10 - PUT /curriculums/{curriculumId}
    제목 및 모듈 수동 수정 또는 AI 재생성
    """
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")

    if request.title:
        c.title = request.title

    if request.modules:
        # 명시된 모듈만 제목/순서 업데이트
        for mod_update in request.modules:
            mod_id = mod_update.get("moduleId")
            if mod_id:
                module = db.query(Module).filter(Module.id == mod_id, Module.curriculum_id == curriculum_id).first()
                if module:
                    if "title" in mod_update:
                        module.title = mod_update["title"]
                    if "week" in mod_update:
                        module.week_number = mod_update["week"]

    c.version += 1
    c.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(c)

    await publish_event("Curriculum.Revised", {
        "curriculum_id": c.id,
        "employee_id": c.employee_id,
        "version": c.version,
    })

    return ApiResponse.ok(
        data=_to_detail(c),
        code="CURRICULUM-200",
        message="커리큘럼이 수정되었습니다.",
    )


# ── 커리큘럼 승인 (api.md §12 - Approval Service 위임 가능) ─────────────

@router.post("/{curriculum_id}/approve")
async def approve_curriculum(curriculum_id: str, request: CurriculumApproveRequest, db: Session = Depends(get_db)):
    """커리큘럼 승인/반려 및 Curriculum.Approved 이벤트 발행"""
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    if c.status not in ("draft", "revised"):
        raise HTTPException(status_code=400, detail=f"Cannot process curriculum with status '{c.status}'")

    if request.action == "APPROVE":
        c.status = "approved"
        c.updated_at = datetime.utcnow()
        db.commit()
        await publish_event("Curriculum.Approved", {
            "curriculum_id": c.id,
            "goal_id": c.goal_id,
            "employee_id": c.employee_id,
            "approved_by": request.comment or "HR",
        })
        return ApiResponse.ok(
            data={"curriculumId": c.id, "status": "APPROVED"},
            code="CURRICULUM-200",
            message="커리큘럼이 승인되었습니다.",
        )
    elif request.action == "REJECT":
        c.status = "rejected"
        c.revision_note = request.comment
        c.updated_at = datetime.utcnow()
        db.commit()
        return ApiResponse.ok(
            data={"curriculumId": c.id, "status": "REJECTED"},
            code="CURRICULUM-200",
            message="커리큘럼이 반려되었습니다.",
        )
    else:
        raise HTTPException(status_code=400, detail="action must be APPROVE or REJECT")


# ── 직원별 커리큘럼 목록 조회 ────────────────────────────────────────

@router.get("/employee/{employee_id}")
def get_curriculums_by_employee(employee_id: str, db: Session = Depends(get_db)):
    cs = db.query(Curriculum).filter(Curriculum.employee_id == employee_id).all()
    return ApiResponse.ok(
        data=[_to_detail(c) for c in cs],
        code="CURRICULUM-200",
        message="커리큘럼 목록 조회 성공",
    )


# ── 모듈 상세 조회 (플랫, curriculum_id 불필요) ──────────────────────

@router.get("/modules/{module_id}")
async def get_module_detail(module_id: str, db: Session = Depends(get_db)):
    """
    GET /curriculums/modules/{moduleId}
    모듈 상세 조회: 설명·학습목표·내용·과제·리소스 반환.
    content가 비어있으면 LLM으로 즉시 생성 후 저장.
    """
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    curriculum = db.query(Curriculum).filter(Curriculum.id == module.curriculum_id).first()

    if not module.content:
        try:
            content = await curriculum_designer_agent.generate_module_content(
                module_title=module.title,
                learning_objectives=module.get_learning_objectives(),
                role=curriculum.role if curriculum else "",
                department=curriculum.department if curriculum else "",
            )
            module.content = content
            db.commit()
        except Exception as e:
            logger.warning(f"[Module] 콘텐츠 생성 실패: {e}")

    return ApiResponse.ok(
        data={
            "moduleId": module.id,
            "curriculumId": module.curriculum_id,
            "week": module.week_number,
            "title": module.title,
            "description": module.description or "",
            "content": module.content or "",
            "learningObjectives": module.get_learning_objectives(),
            "resources": module.get_resources(),
            "assignments": module.get_assignments(),
            "estimatedHours": module.estimated_hours,
        },
        code="CURRICULUM-200",
        message="모듈 상세 조회 성공",
    )


# ── 모듈 콘텐츠 생성 (레거시 호환) ──────────────────────────────────

@router.get("/{curriculum_id}/modules/{module_id}/contents")
async def get_module_content(curriculum_id: str, module_id: str, db: Session = Depends(get_db)):
    """api.md §15 호환 - 학습 콘텐츠 조회 (RAG 기반 생성)"""
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    module = db.query(Module).filter(Module.id == module_id, Module.curriculum_id == curriculum_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    if not module.content:
        content = await curriculum_designer_agent.generate_module_content(
            module_title=module.title,
            learning_objectives=module.get_learning_objectives(),
            role=c.role,
            department=c.department,
        )
        module.content = content
        db.commit()

    return ApiResponse.ok(
        data=[{"contentId": module.id, "title": module.title, "type": "TEXT", "content": module.content}],
        code="LEARNING-200",
        message="학습 콘텐츠 조회 성공",
    )


# ── 커리큘럼 삭제 ────────────────────────────────────────────────────

@router.delete("/{curriculum_id}")
def delete_curriculum(curriculum_id: str, db: Session = Depends(get_db)):
    """DELETE /curriculums/{curriculumId} — HR가 커리큘럼 삭제"""
    c = db.query(Curriculum).filter(Curriculum.id == curriculum_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    db.delete(c)
    db.commit()
    return ApiResponse.ok(
        data={"curriculumId": curriculum_id},
        code="CURRICULUM-200",
        message="커리큘럼이 삭제되었습니다.",
    )


# ── RAG 문서 업로드 ──────────────────────────────────────────────────

class RagUploadRequest(BaseModel):
    texts: list[str]
    metadatas: list[dict] | None = None


@router.post("/rag/documents")
async def upload_rag_documents(request: RagUploadRequest):
    await add_documents(request.texts, request.metadatas)
    return ApiResponse.ok(
        data={"uploaded": len(request.texts)},
        code="COMMON-200",
        message=f"{len(request.texts)}건의 문서가 업로드되었습니다.",
    )
