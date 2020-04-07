import langid
import sys

with open('txt', "r", encoding="utf-8") as fin:
    data = fin.readlines()
a = "{"
b = "}"
mas = []
for line in data:
    words = line.strip().split()
    rus = ""
    eng = ""
    ind = 0
    for i in range(len(words)):
        if ord(words[i][0].lower()) >= ord('а') and ord(words[i][0].lower()) <= ord('я'):
            ind = i
            break
        else:
            eng += words[i] + " "
    rus = " ".join(words[ind:])
    mas.append(f"""{a}"eng": "{eng}", "translate": "{rus}"{b} """)

res = []
for line in mas:
    d = eval(line)
    res.append([d['eng'], d['translate']])
for i in res:
    print(f"""['{i[0]}', '{i[1]}'],""")
