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
    },
    {
        "code": 'print(len("Python"))',
        "output": "6"
    },
    {
        "code": 'print(2 * 3 + 4)',
        "output": "10"
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
        "code": 'print(sum([1, 2, 3]))',
        "output": "6"
    },
    {
        "code": 'print("Hello".lower())',
        "output": "hello"
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
        "code": 'print([i for i in range(3)])',
        "output": "[0, 1, 2]"
    },
    {
        "code": 'print(",".join(["a", "b", "c"]))',
        "output": "a,b,c"
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
        "code": 'print(type(3.5))',
        "output": "<class 'float'>"
    },
    {
        "code": 'print(len([1, [2, 3], 4]))',
        "output": "3"
    },
    {
        "code": 'd = {"a": 1}\nprint(d.get("a"))',
        "output": "1"
    },
    {
        "code": 'print(sorted([3, 1, 2]))',
        "output": "[1, 2, 3]"
    },
    {
        "code": 'print(",".join(map(str, [1, 2, 3])))',
        "output": "1,2,3"
    },
    {
        "code": 'for i in range(3):\n    print(i**2)',
        "output": "0\n1\n4"
    },
    {
        "code": 'print(list(range(1, 4)))',
        "output": "[1, 2, 3]"
    },
    {
        "code": 'print(5 > 3)',
        "output": "True"
    },
    {
        "code": 'print(bool(""))',
        "output": "False"
    },
    {
        "code": 'print("{:.2f}".format(3.14159))',
        "output": "3.14"
    },
    {
        "code": 'print("Py\\\"thon")',
        "output": "Py\"thon"
    },
    {
        "code": 'print(len(set([1, 1, 2])))',
        "output": "2"
    },
    {
        "code": 'print("Hello World".split()[1])',
        "output": "World"
    },
    {
        "code": 'x = [1, 2, 3]\nx.append(4)\nprint(len(x))',
        "output": "4"
    },
    {
        "code": 'print("-".join(["2021", "09", "01"]))',
        "output": "2021-09-01"
    },
    {
        "code": 'print((lambda x: x*2)(3))',
        "output": "6"
    },
    {
        "code": 'for char in "Hi":\n    print(char)',
        "output": "H\ni"
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

