import itertools
import multiprocessing
from flask import Flask, render_template_string, request

app = Flask(__name__)

# 使用可能な数字 (固定順)
DIGITS = [1, 1, 4, 5, 1, 4]
OPERATORS = ['+', '-', '*', '//']  # 除算は整数除算

# 総当たりで数式を生成する関数 (順序固定, 50 並列実行)
def brute_force_equation(target):
    for ops in itertools.product(OPERATORS, repeat=len(DIGITS)-1):
        equation = "".join(str(DIGITS[i]) + ops[i] for i in range(len(ops))) + str(DIGITS[-1])
        try:
            if eval(equation) == target:
                return f"{target} = {equation.replace('//', '/')}"
        except ZeroDivisionError:
            continue
    return None

# 逆算アプローチ（括弧のネストを防ぐ修正）
def reverse_approach(target):
    queue = [(target, str(target))]
    seen = set()
    while queue:
        value, expr = queue.pop()
        if value in seen:
            continue
        seen.add(value)
        if value == eval("".join(map(str, DIGITS))):
            return f"{target} = {expr}"
        for num in DIGITS:
            for op in OPERATORS:
                try:
                    new_expr = f"{expr} {op} {num}" if expr else str(num)
                    new_value = eval(new_expr)
                    queue.append((new_value, new_expr))
                except ZeroDivisionError:
                    continue
    return None

# 並列処理で計算する関数
def parallel_compute(target):
    with multiprocessing.Pool(processes=10) as pool:
        results = pool.map(brute_force_equation, [target] * 10)
        results.append(reverse_approach(target))  # 逆算アプローチは単独で実行
        for result in results:
            if result:
                return result
    return None

# Web ページのルート
template = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>114514 数式ジェネレーター</title>
</head>
<body>
    <h1>114514 の数字だけを使った数式ジェネレーター</h1>
    <form method="GET">
        <label for="target">ターゲットの数値: </label>
        <input type="number" id="target" name="target" required>
        <button type="submit">生成</button>
    </form>
    {% if result %}
        <h2>{{ result }}</h2>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    target = request.args.get("target")
    result = None
    if target:
        try:
            target = int(target)
            result = parallel_compute(target)
        except ValueError:
            result = "無効な入力です"
    return render_template_string(template, result=result)

if __name__ == '__main__':
    app.run(debug=True)
