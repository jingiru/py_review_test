import os
import time
import random
import json
from typing import List, Dict, Any

import gspread
from google.oauth2.service_account import Credentials
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ===== 환경변수 =====
SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")  # 필수
SA_JSON   = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # 필수

# ===== 캐시 =====
_questions_cache: List[Dict[str, Any]] = []
_cache_loaded_at = 0.0
_CACHE_TTL = 60  # 초. 5분마다 새로고침


# ===== 유틸 =====
def _normalize(s: str) -> str:
    """비교용 단순 정규화: 앞뒤 공백 제거 + 소문자"""
    return (s or "").strip().lower()


# ===== Google Sheets 클라이언트 =====
def _gs_client():
    if not SA_JSON:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON 미설정")
    if not SHEETS_ID:
        raise RuntimeError("GOOGLE_SHEETS_ID 미설정")

    info = json.loads(SA_JSON)
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)


# ===== 시트 -> 문제 로드 (헤더 다국어/중복 안전 처리) =====
def load_questions_from_sheet(force: bool = False) -> List[Dict[str, Any]]:
    """
    시트 '확정'에서 전체 문제를 읽어 캐시에 저장하고 반환한다.
    헤더는 영/한 혼용을 허용하며, code/output/difficulty/type 를 추출한다.
    """
    global _questions_cache, _cache_loaded_at

    now = time.time()
    if (now - _cache_loaded_at < _CACHE_TTL) and _questions_cache and not force:
        return _questions_cache

    gc = _gs_client()
    sh = gc.open_by_key(SHEETS_ID)
    ws = sh.worksheet("확정")  # 워크시트 이름 고정(필요시 변경)

    values = ws.get_all_values()  # 2차원 리스트
    if not values:
        _questions_cache = []
        _cache_loaded_at = now
        return _questions_cache

    header = values[0] if values else []

    # 우리가 찾을 헤더 후보(영문/한글 모두 지원)
    def find_index(candidates: List[str]):
        for name in candidates:
            if name in header:
                # 동일한 이름이 여러 번 있어도 첫 번째만 사용
                return header.index(name)
        return None

    idx_code = find_index(["code", "코드", "문제", "문항"])
    idx_out  = find_index(["output", "정답", "예상출력", "답"])
    idx_diff = find_index(["difficulty", "난이도", "예상 난이도", "level"])
    idx_type = find_index(["type", "유형", "분야", "category", "분류"])

    rows: List[Dict[str, Any]] = []

    for r in values[1:]:
        # 메타 데이터(난이도/유형)는 trim, code/output은 공백 보존
        def cell_trim(idx):
            return (r[idx].strip() if idx is not None and idx < len(r) else "")
        def cell_raw(idx):
            return (r[idx] if idx is not None and idx < len(r) else "")

        code       = cell_raw(idx_code)
        output     = cell_raw(idx_out)
        difficulty = cell_trim(idx_diff)
        qtype      = cell_trim(idx_type)

        # code & output 둘 다 비면 스킵 (빈 행)
        if not code and not output:
            continue

        rows.append({
            "code": code,
            "output": output,
            "difficulty": difficulty,  # 원본 보존
            "type": qtype,             # 원본 보존
        })

    _questions_cache = rows
    _cache_loaded_at = now
    return _questions_cache


def _filter_questions(questions: List[Dict[str, Any]], difficulty: str, qtype: str) -> List[Dict[str, Any]]:
    """
    difficulty, qtype 중 주어진 값만 AND 조건으로 필터링.
    빈 문자열("") 또는 "all"은 해당 필터 미적용.
    """
    nd = _normalize(difficulty)
    nt = _normalize(qtype)

    def matches(q):
        ok = True
        if nd and nd != "all":
            ok = ok and (_normalize(q.get("difficulty")) == nd)
        if nt and nt != "all":
            ok = ok and (_normalize(q.get("type")) == nt)
        return ok

    if (not nd or nd == "all") and (not nt or nt == "all"):
        return questions

    return [q for q in questions if matches(q)]


def pick_question(difficulty: str = "all", qtype: str = "all") -> Dict[str, Any]:
    questions = load_questions_from_sheet(force=False)
    pool = _filter_questions(questions, difficulty, qtype)

    # 필터 결과가 없으면 전체에서 랜덤(UX 안전장치)
    if not pool:
        pool = questions

    if not pool:
        return {"code": "print('시트가 비었습니다')", "output": ""}

    return random.choice(pool)


# ===== 라우팅 =====
@app.route("/")
def index():
    q = pick_question()
    return render_template("index.html", code=q["code"], output=q["output"])


@app.get("/next")
def next_question():
    """
    기존 프론트 호환용: 난이도/유형 필터를 적용해 랜덤 1문제 반환
    /next?difficulty=easy&type=리스트
    """
    difficulty = request.args.get("difficulty", "all")
    qtype      = request.args.get("type", "all")
    q = pick_question(difficulty, qtype)
    return jsonify({"code": q["code"], "output": q["output"]})


@app.get("/api/questions")
def api_questions():
    """
    새 API: 필터 적용 후 '목록' 반환(프론트에서 버튼 누를 때 사용)
    /api/questions?difficulty=easy&type=리스트
    force=1 로 캐시 무시하고 새로 로드 가능
    """
    difficulty = request.args.get("difficulty", "").strip()
    qtype      = request.args.get("type", "").strip()
    force      = request.args.get("force", "0") == "1"

    questions = load_questions_from_sheet(force=force)
    filtered  = _filter_questions(questions, difficulty, qtype)
    return jsonify(filtered)


@app.get("/api/filters")
def api_filters():
    """
    시트에서 실제 존재하는 난이도/유형 값 목록을 내려줌.
    프론트에서 버튼을 동적으로 만들 때 유용.
    """
    questions = load_questions_from_sheet(force=False)
    diffs = sorted({(q.get("difficulty") or "").strip() for q in questions if (q.get("difficulty") or "").strip()})
    types = sorted({(q.get("type") or "").strip() for q in questions if (q.get("type") or "").strip()})
    return jsonify({"difficulties": diffs, "types": types})


# (옵션) 헬스체크
@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    # 최초 기동 시 강제 로드(배포 직후 즉시 반영)
    load_questions_from_sheet(force=True)
    app.run(debug=True, host="0.0.0.0", port=5000)
