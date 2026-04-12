"""
dummy/ 폴더의 PDF 파일을 각 에이전트의 RAG에 임베딩하는 테스트 스크립트

실행 전제:
  - docker-compose up으로 서비스가 기동된 상태
  - pypdf, requests 설치: pip install pypdf requests

Python 에이전트 직접 호출 (gateway는 해당 경로를 Spring Boot로 라우팅):
  - goal-setter-agent  :10021  (신입사원 지원서 PDF 4개)
  - curriculum-designer-agent :10022  (강의자료 PDF)
  - ai-tutor-agent     :10024  (강의자료 PDF)
"""

import io
import os
import sys
import unicodedata
import requests
from pathlib import Path


def _contains(filename: str, keyword: str) -> bool:
    """macOS NFD 인코딩을 고려한 한글 파일명 포함 여부 확인"""
    return unicodedata.normalize("NFD", keyword) in unicodedata.normalize("NFD", filename)

try:
    from pypdf import PdfReader
except ImportError:
    print("pypdf가 설치되어 있지 않습니다. 설치 후 다시 실행하세요:")
    print("  pip install pypdf requests")
    sys.exit(1)

DUMMY_DIR = Path(__file__).parent / "dummy"

GOAL_AGENT     = "http://localhost:10021"
CURRICULUM_AGENT = "http://localhost:10022"
TUTOR_AGENT    = "http://localhost:10024"

CHUNK_SIZE    = 800
CHUNK_OVERLAP = 100


def chunk_text(text: str) -> list[str]:
    chunks, start = [], 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()
        if len(chunk) > 50:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)
    return "\n".join(pages)


def ok(label: str, msg: str):
    print(f"  [OK] {label}: {msg}")


def fail(label: str, msg: str):
    print(f"  [FAIL] {label}: {msg}")


# ─────────────────────────────────────────────────────────────
# 1. goal-setter-agent — 신입사원 지원서 PDF 업로드
# ─────────────────────────────────────────────────────────────

def ingest_employee_pdfs():
    print("\n[1] goal-setter-agent — 신입사원 지원서 임베딩")
    print(f"    endpoint: POST {GOAL_AGENT}/goals/ingest/pdf")

    profile_pdfs = sorted(p for p in DUMMY_DIR.glob("*.pdf") if _contains(p.name, "지원서"))
    if not profile_pdfs:
        fail("goal-setter-agent", "dummy/ 폴더에 지원서 PDF가 없습니다.")
        return False

    success = 0
    for pdf_path in profile_pdfs:
        # 파일명에서 이름 추출: 김규리_지원서_20260409.pdf → 김규리
        employee_name = pdf_path.stem.split("_")[0]

        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            data = {
                "employee_id": "",
                "employee_name": employee_name,
                "department": "",
                "role": "",
            }
            try:
                resp = requests.post(
                    f"{GOAL_AGENT}/goals/ingest/pdf",
                    files=files,
                    data=data,
                    timeout=60,
                )
            except requests.exceptions.ConnectionError:
                fail(pdf_path.name, f"연결 실패 — {GOAL_AGENT} 에 접근할 수 없습니다.")
                continue
            except Exception as e:
                fail(pdf_path.name, str(e))
                continue

        if resp.status_code == 200:
            d = resp.json().get("data", {})
            ok(pdf_path.name, f"{d.get('total_chunks', '?')}청크 저장 (페이지: {d.get('total_pages', '?')})")
            success += 1
        else:
            fail(pdf_path.name, f"HTTP {resp.status_code} — {resp.text[:200]}")

    print(f"    → {success}/{len(profile_pdfs)} 성공")
    return success == len(profile_pdfs)


# ─────────────────────────────────────────────────────────────
# 2. curriculum-designer-agent — 강의자료 PDF 업로드
# ─────────────────────────────────────────────────────────────

def ingest_curriculum_pdf():
    print("\n[2] curriculum-designer-agent — 강의자료 임베딩")
    print(f"    endpoint: POST {CURRICULUM_AGENT}/curriculums/rag/documents")

    lecture_pdfs = sorted(p for p in DUMMY_DIR.glob("*.pdf") if not _contains(p.name, "지원서"))

    if not lecture_pdfs:
        fail("curriculum-designer-agent", "dummy/ 폴더에 강의자료 PDF가 없습니다.")
        return False

    success = 0
    for pdf_path in lecture_pdfs:
        print(f"    파싱 중: {pdf_path.name}")
        try:
            full_text = extract_pdf_text(pdf_path)
        except Exception as e:
            fail(pdf_path.name, f"PDF 파싱 실패: {e}")
            continue

        chunks = chunk_text(full_text)
        print(f"    → {len(chunks)}개 청크 생성")

        metadatas = [{"source": pdf_path.name, "type": "lecture_material", "chunk": i} for i in range(len(chunks))]
        payload = {"texts": chunks, "metadatas": metadatas}

        try:
            resp = requests.post(
                f"{CURRICULUM_AGENT}/curriculums/rag/documents",
                json=payload,
                timeout=120,
            )
        except requests.exceptions.ConnectionError:
            fail(pdf_path.name, f"연결 실패 — {CURRICULUM_AGENT} 에 접근할 수 없습니다.")
            continue
        except Exception as e:
            fail(pdf_path.name, str(e))
            continue

        if resp.status_code == 200:
            d = resp.json().get("data", {})
            ok(pdf_path.name, f"{d.get('uploaded', '?')}건 저장")
            success += 1
        else:
            fail(pdf_path.name, f"HTTP {resp.status_code} — {resp.text[:200]}")

    return success == len(lecture_pdfs)


# ─────────────────────────────────────────────────────────────
# 3. ai-tutor-agent — 강의자료 PDF 업로드
# ─────────────────────────────────────────────────────────────

def ingest_tutor_pdf():
    print("\n[3] ai-tutor-agent — 강의자료 임베딩")
    print(f"    endpoint: POST {TUTOR_AGENT}/tutor/rag/documents")

    lecture_pdfs = sorted(p for p in DUMMY_DIR.glob("*.pdf") if not _contains(p.name, "지원서"))

    if not lecture_pdfs:
        fail("ai-tutor-agent", "dummy/ 폴더에 강의자료 PDF가 없습니다.")
        return False

    success = 0
    for pdf_path in lecture_pdfs:
        print(f"    파싱 중: {pdf_path.name}")
        try:
            full_text = extract_pdf_text(pdf_path)
        except Exception as e:
            fail(pdf_path.name, f"PDF 파싱 실패: {e}")
            continue

        chunks = chunk_text(full_text)
        print(f"    → {len(chunks)}개 청크 생성")

        metadatas = [{"source": pdf_path.name, "type": "lecture_material", "chunk": i} for i in range(len(chunks))]
        payload = {"texts": chunks, "metadatas": metadatas}

        try:
            resp = requests.post(
                f"{TUTOR_AGENT}/tutor/rag/documents",
                json=payload,
                timeout=120,
            )
        except requests.exceptions.ConnectionError:
            fail(pdf_path.name, f"연결 실패 — {TUTOR_AGENT} 에 접근할 수 없습니다.")
            continue
        except Exception as e:
            fail(pdf_path.name, str(e))
            continue

        if resp.status_code == 200:
            d = resp.json().get("data", {})
            ok(pdf_path.name, f"{d.get('uploaded', '?')}건 저장")
            success += 1
        else:
            fail(pdf_path.name, f"HTTP {resp.status_code} — {resp.text[:200]}")

    return success == len(lecture_pdfs)


# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  PDF → Qdrant 임베딩 테스트")
    print(f"  dummy 폴더: {DUMMY_DIR}")
    print("=" * 55)

    all_files = list(DUMMY_DIR.glob("*.pdf"))
    print(f"\n발견된 PDF 파일 ({len(all_files)}개):")
    for f in sorted(all_files):
        print(f"  - {f.name}")

    r1 = ingest_employee_pdfs()
    r2 = ingest_curriculum_pdf()
    r3 = ingest_tutor_pdf()

    print("\n" + "=" * 55)
    print("  결과 요약")
    print("=" * 55)
    print(f"  goal-setter-agent (신입사원 지원서): {'성공' if r1 else '실패'}")
    print(f"  curriculum-designer-agent (강의자료): {'성공' if r2 else '실패'}")
    print(f"  ai-tutor-agent (강의자료):            {'성공' if r3 else '실패'}")
    print()
    if r1 and r2 and r3:
        print("  전체 성공!")
        print("  Qdrant 대시보드: http://localhost:6333/dashboard")
    else:
        print("  일부 실패 — 에이전트 로그를 확인하세요:")
        print("    docker compose logs goal-setter-agent --tail 30")
        print("    docker compose logs curriculum-designer-agent --tail 30")
        print("    docker compose logs ai-tutor-agent --tail 30")
        sys.exit(1)
