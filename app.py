import os
import time
import random
import json

import gspread
from google.oauth2.service_account import Credentials
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ===== 환경변수 =====
SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")  # 필수
SA_JSON   = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # 필수

_questions_cache = []
_cache_loaded_at = 0
_CACHE_TTL = 300  # 초. 5분마다 새로고침


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

# ===== 시트 -> 문제 로드 (헤더 중복/다국어 안전 처리) =====
def _normalize_difficulty(val: str) -> str:
    v = (val or "").strip().lower()
    return v

def load_questions_from_sheet(force: bool = False):
    global _questions_cache, _cache_loaded_at

    # 캐시 TTL 내면 재사용
    now = time.time()
    if (now - _cache_loaded_at < CACHE_TTL) and _questions_cache and not force:
        return

    gc = _gs_client()
    sh = gc.open_by_key(SHEETS_ID)
    ws = sh.worksheet(TAB_NAME)  # 원하는 탭만 읽기

    # 모든 값을 통으로 받아, 헤더를 직접 파싱해 중복 헤더 문제 회피
    values = ws.get_all_values()  # 2차원 리스트
    if not values:
        _questions_cache = []
        _cache_loaded_at = now
        return

    header = values[0]

    # 우리가 찾을 헤더 후보(영문/한글 모두 지원)
    def find_index(candidates):
        for name in candidates:
            if name in header:
                # 동일한 이름이 여러 번 있어도 첫 번째만 사용
                return header.index(name)
        return None

    idx_diff = find_index(["difficulty", "예상 난이도"])
    idx_type = find_index(["type", "분야"])
    idx_code = find_index(["code", "문제"])
    idx_out  = find_index(["output", "답"])

    rows = []
    for r in values[1:]:
        def cell(idx):
            return (r[idx].strip() if idx is not None and idx < len(r) else "")

        difficulty = _normalize_difficulty(cell(idx_diff))
        qtype      = cell(idx_type)
        code       = cell(idx_code)
        output     = cell(idx_out)

        # 빈 행은 스킵
        if not code and not output:
            continue

        rows.append({
            "difficulty": difficulty,
            "type": qtype,
            "code": code,
            "output": output,
        })

    _questions_cache = rows
    _cache_loaded_at = now


def pick_question(difficulty="all", qtype="all"):
    load_questions_from_sheet()
    pool = _questions_cache

    if difficulty and difficulty != "all":
        pool = [q for q in pool if q.get("difficulty") == difficulty]
    if qtype and qtype != "all":
        pool = [q for q in pool if q.get("type") == qtype]

    if not pool:
        pool = _questions_cache

    if not pool:
        return {"code": "print('시트가 비었습니다')", "output": ""}

    return random.choice(pool)


# ===== 라우팅 =====
@app.route("/")
def index():
    q = pick_question()
    return render_template("index.html", code=q["code"], output=q["output"])

@app.route("/next")
def next_question():
    difficulty = request.args.get("difficulty", "all")
    qtype = request.args.get("type", "all")
    q = pick_question(difficulty, qtype)
    return jsonify({"code": q["code"], "output": q["output"]})

# (옵션) 헬스체크
@app.route("/healthz")
def healthz():
    return "ok", 200


if __name__ == "__main__":
    # 최초 로딩 시 강제 새로고침
    load_questions_from_sheet(force=True)
    app.run(debug=True, host="0.0.0.0", port=5000)