from flask import Flask, render_template
import random
import io
import contextlib
import codecs

def is_correct(user_input: str, expected_output: str) -> bool:
    # expected_output: 이스케이프 문자로 저장된 정답 ex) '1\\n2\\n3'
    # user_input: 실제 줄바꿈으로 입력된 문자열 ex) '1\n2\n3'
    
    # 정답 문자열을 실제 개행 포함 형태로 디코딩
    decoded_expected = codecs.decode(expected_output, 'unicode_escape')
    
    # 비교 (공백 제거)
    return user_input.strip() == decoded_expected.strip()


app = Flask(__name__)

# 문제 리스트 (코드와 예상 출력 짝)
questions = [
    {
        "code": 'print(10 * 2)',
        "output": "20"
    },
    {
        "code": 'print("Hello, Python!")',
        "output": "Hello, Python!"
    },
    {
        "code": 'print("100")',
        "output": "100"
    },
    {
        "code": 'print(500)',
        "output": "500"
    },
    {
        "code": 'print("num", 1000)',
        "output": "num 1000"
    },
    {
        "code": 'print("hi"*10)',
        "output": "hihihihihihihihihihi"
    },
    {
        "code": 'print("hello "*3)',
        "output": "hello hello hello"
    },
    {
        "code": 'print("python")',
        "output": "python"
    },
    {
        "code": 'print(3 + 4)',
        "output": "7"
    },
    {
        "code": 'print(2 * 3 + 4)',
        "output": "10"
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
        "code": 'print(1)\nprint(2)\nprint(3)',
        "output": "1\n2\n3"
    },
    {
        "code": 'x = [1, 2, 3]\nprint(x[1])',
        "output": "2"
    },
    {
        "code": 'print("Py" + "thon")',
        "output": "Python"
    },
    {
        "code": 'for i in range(1, 4):\n    print("A" * i)',
        "output": "A\nAA\nAAA"
    },
    {
        "code": 'a = input() # 10 입력\nprint(a*2)',
        "output": "1010"
    },
    {
        "code": "ace='10'\nbye='200'\nsum=ace+bye\nprint(sum)",
        "output": "10200"
    },
    {
        "code": 'print(len("Python"))',
        "output": "6"
    },
    {
        "code": 'print(sum([1, 2, 3]))',
        "output": "6"
    },
    {
        "code": 'print(10 // 3)',
        "output": "3"
    },
    {
        "code": 'print(10 % 3)',
        "output": "1"
    },
    {
        "code": 'for i in range(3)\n    print(i)',
        "output": "0\n1\n2"
    },
    {
        "code": 'print(min(5, 7, 2))',
        "output": "2"
    },
    {
        "code": 'print(max([1, 5, 3]))',
        "output": "5"
    },
    {
        "code": 'for i in range(3):\n    print(i**2)',
        "output": "0\n1\n4"
    },
    {
        "code": 'A = 1\nresult = 0\nwhile A < = 15:\n    if not A % 2:\n        result += A\n    A += 1\nprint(result)',
        "output": "56"
    },
    {
        "code": 'age = int(input()) # 19 입력\nstudent = input() # Y 입력\n\nif age < 19 and student == ‘Y’:\n    print(‘청소년 학생 할인 적용’)\nelif age < 19 or student == ‘Y’:\n    print(‘부분 할인 적용’)\nelse:\n    print(‘할인 대상 아님’)',
        "output": "부분 할인 적용"
    },
    {
        "code": "data=['파이썬',['코딩','은','재미','있','다'],'배우자']\n"
                "data[1][2]='도전'\n"
                "data[1][3:5]=['해','보자']\n"
                "print(data[1][2:4])",
        "output": "['도전', '해']"
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

@app.route("/next")
def next_question():
    problem = random.choice(questions)
    return {
        "code": problem["code"],
        "output": problem["output"]
    }


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

