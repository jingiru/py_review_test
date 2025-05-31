from flask import Flask, render_template
import random
import io
import contextlib

app = Flask(__name__)

# 문제 리스트 (코드와 예상 출력 짝)
questions = [
    {
        "code": 'print("Hello, Python!")',
        "output": "Hello, Python!"
    },
    {
        "code": 'print(3 + 4)',
        "output": "7"
    },
    {
        "code": 'for i in range(2):\n    print("Hi")',
        "output": "Hi\nHi"
    },
    {
        "code": 'print("A" * 3)',
        "output": "AAA"
    },
    {
        "code": 'print("1\\n2\\n3")',
        "output": "1\n2\n3"
    }
]

@app.route("/")
def index():
    # 랜덤 문제 선택
    problem = random.choice(questions)
    return render_template(
        "index.html",
        code=problem["code"],
        output=problem["output"]
    )

if __name__ == "__main__":
    app.run(debug=True)
