document.addEventListener("DOMContentLoaded", () => {
    const checkBtn = document.getElementById("check-answer");
    const userInput = document.getElementById("user-answer");
    const resultMessage = document.getElementById("result-message");

    checkBtn.addEventListener("click", () => {
        // 입력값과 실제 출력 비교
        const userAnswer = userInput.value.trim();

        if (userAnswer === actualOutput) {
            resultMessage.textContent = "✅ 정답입니다! 잘했어요!";
            resultMessage.style.color = "#2e7d32"; // 초록색
        } else {
            resultMessage.textContent = `❌ 오답입니다. 다시 생각해보세요.\n(정답: ${actualOutput})`;
            resultMessage.style.color = "#c62828"; // 빨간색
        }
    });
});
