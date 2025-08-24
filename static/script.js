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

    // 정답(시트에서 온 값)을 저장할 변수 (엄격 비교)
    let actualOutput = "";

    // 문제 새로고침 함수
    const loadNewQuestion = async () => {
        const res = await fetch("/next", { cache: "no-store" });
        const data = await res.json();

        // 코드 변경
        document.getElementById("python-code").textContent = data.code;

        // 정답 업데이트 (시트가 실제 개행/공백을 포함해 내려주므로 그대로 사용)
        actualOutput = data.output;

        // 입력창과 결과 초기화
        userInput.value = "";
        userInput.focus();
        resultMessage.textContent = "정답 확인하기 버튼을 눌러보세요!";
        resultContainer.classList.remove("result-correct", "result-incorrect");
    };

    checkBtn.addEventListener("click", () => {
        // 공백/개행까지 포함한 사용자 입력 (trim 제거)
        const userAnswer = userInput.value;

        // 결과 컨테이너의 기존 클래스 제거
        resultContainer.classList.remove("result-correct", "result-incorrect");

        // 엄격 비교 (끝 공백 포함 완전 일치)
        if (userAnswer === actualOutput) {
            resultMessage.textContent = "🎉 정답입니다! 완벽해요!";
            resultContainer.classList.add("result-correct");

            triggerFireworks();

            // 0.5초 후 자동 새 문제 로딩
            setTimeout(loadNewQuestion, 500);
        } else {
            resultMessage.textContent = "❌ 아쉽게도 틀렸습니다. 다시 한번 생각해보세요!";
            resultContainer.classList.add("result-incorrect");
        }

        // 결과 메시지 원래대로 복구
        setTimeout(() => {
            resultMessage.textContent = "정답 확인하기 버튼을 눌러보세요!";
            resultContainer.classList.remove("result-correct", "result-incorrect");
        }, 850);

        // 결과 영역으로 부드럽게 스크롤
        resultContainer.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
    });

    // '다른 문제 도전하기' 버튼 기능
    nextBtn.addEventListener("click", loadNewQuestion);

    // Ctrl+Enter 단축키로 정답 확인
    userInput.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "Enter") {
            checkBtn.click();
        }
    });
});
