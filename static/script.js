document.addEventListener("DOMContentLoaded", () => {
    const checkBtn = document.getElementById("check-answer");
    const nextBtn = document.getElementById("next-question");
    const userInput = document.getElementById("user-answer");
    const resultMessage = document.getElementById("result-message");
    const resultContainer = document.getElementById("result-container");


    // 문제 새로고침 함수
    const loadNewQuestion = async () => {
        const res = await fetch("/next");
        const data = await res.json();

        // 코드 변경
        document.getElementById("python-code").textContent = data.code;

        // 정답 업데이트
        actualOutput = data.output;

        // 입력창과 결과 초기화
        userInput.value = "";  // 변수 그대로 사용
        userInput.focus();
        resultMessage.textContent = "정답 확인하기 버튼을 눌러보세요!";
        resultContainer.classList.remove("result-correct", "result-incorrect");
    };

    
    // 이스케이프 문자열을 실제 개행 등으로 변환
    function decodeEscapedString(str) {
        return str
            .replace(/\\\\/g, "\\") // 먼저 \\ → \
            .replace(/\\n/g, "\n")  // \n → 줄바꿈
            .replace(/\\t/g, "\t")  // \t → 탭
            .replace(/\\r/g, "\r")  // \r → 캐리지리턴
            .replace(/\\"/g, "\"")  // \" → "
            .replace(/\\'/g, "'");  // \' → '
    }

    checkBtn.addEventListener("click", () => {
        const userAnswer = userInput.value.trim();

        // 결과 컨테이너의 기존 클래스 제거
        resultContainer.classList.remove("result-correct", "result-incorrect");

        if (userAnswer === actualOutput) {
            resultMessage.textContent = "🎉 정답입니다! 완벽해요!";
            resultContainer.classList.add("result-correct");

            // 1.5초 후 자동 새 문제 로딩
            setTimeout(loadNewQuestion, 500);
        } else {
            resultMessage.textContent = `❌ 아쉽게도 틀렸습니다. 다시 한번 생각해보세요!`;
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

    // Ctrl+Enter 단축키로 정답 확인 (Ctrl+Enter)
    userInput.addEventListener("keydown", (e) => {
        if (e.ctrlKey && e.key === "Enter") {
            checkBtn.click();
        }
    });
});