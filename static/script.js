function triggerFireworks() {
    const canvas = document.getElementById('fireworks-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const particleCount = 100;

    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: canvas.width / 2,
            y: canvas.height / 2,
            radius: Math.random() * 3 + 2,
            color: `hsl(${Math.random() * 360}, 100%, 70%)`,
            angle: Math.random() * 2 * Math.PI,
            speed: Math.random() * 5 + 2,
            alpha: 1
        });
    }

    const interval = setInterval(() => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(p => {
            p.x += Math.cos(p.angle) * p.speed;
            p.y += Math.sin(p.angle) * p.speed;
            p.alpha -= 0.02;

            ctx.beginPath();
            ctx.globalAlpha = p.alpha;
            ctx.fillStyle = p.color;
            ctx.arc(p.x, p.y, p.radius, 0, 2 * Math.PI);
            ctx.fill();
        });

        if (particles.every(p => p.alpha <= 0)) {
            clearInterval(interval);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    }, 16);
}

document.addEventListener("DOMContentLoaded", () => {
    const checkBtn = document.getElementById("check-answer");
    const nextBtn = document.getElementById("next-question");
    const userInput = document.getElementById("user-answer");
    const resultMessage = document.getElementById("result-message");
    const resultContainer = document.getElementById("result-container");
    const codeEl = document.getElementById("python-code");
    const filtersSection = document.querySelector(".filters-section");

    // --- 필터 상태 관리 (localStorage 복원 포함) ---
    const DEFAULT_STATE = { difficulty: "all", type: "all" };  
    const state = { ...DEFAULT_STATE };   

    /*
    기존 필터 저장부
    const loadPersistedState = () => {
        try {
            const saved = JSON.parse(localStorage.getItem("pyquiz.filters") || "{}");
            return { ...DEFAULT_STATE, ...saved };
        } catch {
            return { ...DEFAULT_STATE };
        }
    };
    const state = { ...DEFAULT_STATE };
    localStorage.removeItem("pyquiz.filters");

    const persistState = () => {
        localStorage.setItem("pyquiz.filters", JSON.stringify(state));
    };
    */

    // --- 그룹 내 버튼 active/aria 토글 ---
    function activateButtonInGroup(groupEl, valueToActivate) {
        groupEl.querySelectorAll("button.pill-btn").forEach(btn => {
            const isActive = btn.dataset.value === valueToActivate;
            btn.classList.toggle("is-active", isActive);
            btn.setAttribute("aria-pressed", String(isActive));
        });
    }

    // --- 초기 UI에 저장된 state 반영 ---
    function syncFilterButtonsFromState() {
        if (!filtersSection) return;
        const groups = filtersSection.querySelectorAll(".filter-group");
        groups.forEach(group => {
            const kind = group.querySelector(".filter-buttons button")?.dataset.filterKind;
            if (!kind) return;
            const targetVal = state[kind] ?? "all";
            activateButtonInGroup(group, targetVal);
        });
    }

    // 서버에서 index.html이 내려준 전역값 사용 (초기 문제용)
    let expected = window.actualOutput ?? "";

    // 공통: 결과 영역 초기화
    function resetResultUI() {
        userInput.value = "";
        userInput.focus();
        resultMessage.textContent = "정답 확인하기 버튼을 눌러보세요!";
        resultContainer.classList.remove("result-correct", "result-incorrect");
    }

    // 현재 state로 /next 호출 URL 생성
    function buildNextUrl() {
        const params = new URLSearchParams();
        params.set("difficulty", state.difficulty || "all");
        params.set("type", state.type || "all");
        return `/next?${params.toString()}`;
    }

    // 문제 새로고침 함수(필터 반영)
    const loadNewQuestion = async () => {
        const url = buildNextUrl();
        const res = await fetch(url, { cache: "no-store" });
        if (!res.ok) {
            console.error("문제 로딩 실패:", res.status);
            return;
        }
        const data = await res.json();

        // 코드/정답 반영
        codeEl.textContent = data.code;
        expected = data.output;

        resetResultUI();
    };

    // 필터 버튼 바인딩: 클릭 시 state 갱신 + 저장 + 즉시 새 문제 로드
    if (filtersSection) {
        filtersSection.addEventListener("click", (e) => {
            const btn = e.target.closest("button.pill-btn");
            if (!btn) return;
            const kind = btn.dataset.filterKind; // "difficulty" | "type"
            const value = btn.dataset.value ?? "all";
            if (!kind) return;

            // 같은 그룹 내 활성화 갱신
            const groupEl = btn.closest(".filter-group");
            if (groupEl) activateButtonInGroup(groupEl, value);

            // 상태 갱신 + 저장
            state[kind] = value;

            // 새 문제 로드
            loadNewQuestion();
        });
    }

    // 정답 확인
    checkBtn.addEventListener("click", () => {
        const userAnswer = userInput.value; // 공백/개행 포함 그대로 비교
        resultContainer.classList.remove("result-correct", "result-incorrect");

        if (userAnswer === expected) {
            resultMessage.textContent = "🎉 정답입니다! 완벽해요!";
            resultContainer.classList.add("result-correct");
            triggerFireworks();

            // 0.5초 후 자동 새 문제 로딩 (현재 필터 유지)
            setTimeout(loadNewQuestion, 500);
        } else {
            resultMessage.textContent = "❌ 아쉽게도 틀렸습니다. 다시 한번 생각해보세요!";
            resultContainer.classList.add("result-incorrect");
        }

        // 결과 메시지 복구
        setTimeout(() => {
            resultMessage.textContent = "정답 확인하기 버튼을 눌러보세요!";
            resultContainer.classList.remove("result-correct", "result-incorrect");
        }, 850);

        // 결과 영역으로 부드럽게 스크롤
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });

    // '다른 문제 도전하기' 버튼: 현재 필터로 새 문제
    nextBtn.addEventListener("click", loadNewQuestion);

    // Ctrl+Enter 단축키로 정답 확인
    userInput.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "Enter") {
            checkBtn.click();
        }
    });

    // 초기: 저장된 필터 상태를 UI에 반영하고, 현재 코드/정답은 그대로 두되
    // 사용자가 바로 '다른 문제 도전하기'를 누르면 필터가 적용된 문제가 나오도록 준비
    syncFilterButtonsFromState();
});
