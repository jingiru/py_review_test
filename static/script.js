document.addEventListener("DOMContentLoaded", () => {
    const checkBtn = document.getElementById("check-answer");
    const userInput = document.getElementById("user-answer");
    const resultMessage = document.getElementById("result-message");
    const resultContainer = document.getElementById("result-container");

    checkBtn.addEventListener("click", () => {
        const userAnswer = userInput.value.trim();

        // 결과 컨테이너의 기존 클래스 제거
        resultContainer.classList.remove("result-correct", "result-incorrect");

        if (userAnswer === actualOutput) {
            resultMessage.textContent = "🎉 정답입니다! 완벽해요!";
            resultContainer.classList.add("result-correct");
        } else {
            resultMessage.textContent = `❌ 아쉽게도 틀렸습니다. 다시 한번 생각해보세요!`;
            resultContainer.classList.add("result-incorrect");
        }

        // 결과 영역으로 부드럽게 스크롤
        resultContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
    });

    // 엔터키로 정답 확인 (Ctrl+Enter)
    userInput.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "Enter") {
            checkBtn.click();
        }
    });
});