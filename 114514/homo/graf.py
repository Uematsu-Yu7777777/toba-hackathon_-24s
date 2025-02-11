import re
import matplotlib.pyplot as plt

# homo.js ファイルの内容を読み込む
with open(r'C:\Users\MgO2\Documents\GitHub\JP-tlanstlator\114514\homo\homo.js', 'r', encoding='utf-8') as file:
    js_content = file.read()

# homo 関数の定義部分を抽出
homo_function_content = re.search(r'const homo = \(\(Nums\) => {(.+?)}\)\(\{(.+?)\}\);', js_content, re.DOTALL)
if homo_function_content:
    homo_function_content = homo_function_content.group(2)
else:
    raise ValueError("homo 関数の定義部分が見つかりませんでした。")

# 数値とその表現を辞書に格納
nums_dict = {}
for line in homo_function_content.split(',\n'):
    match = re.match(r'\s*(\d+|["⑨"]):\s*"(.+?)"', line)
    if match:
        num = match.group(1)
        if num.isdigit():
            num = int(num)
        expression = match.group(2)
        nums_dict[num] = expression

# 1から5000までの数値に対して *, +, -, / の使用回数をカウント
counts = {'*': [], '+': [], '-': [], '/': []}
for i in range(1, 5001):
    if i in nums_dict:
        expression = nums_dict[i]
        counts['*'].append(expression.count('*'))
        counts['+'].append(expression.count('+'))
        counts['-'].append(expression.count('-'))
        counts['/'].append(expression.count('/'))
    else:
        counts['*'].append(0)
        counts['+'].append(0)
        counts['-'].append(0)
        counts['/'].append(0)

# グラフを描画
x = range(1, 5001)
plt.figure(figsize=(14, 7))

plt.plot(x, counts['*'], label='*', color='blue')
plt.plot(x, counts['+'], label='+', color='green')
plt.plot(x, counts['-'], label='-', color='red')
plt.plot(x, counts['/'], label='/', color='purple')

plt.xlabel('Number')
plt.ylabel('Count')
plt.title('Distribution of *, +, -, / Usage from 1 to 5000')
plt.legend()
plt.grid(True)
plt.show()