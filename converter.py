import langid
import sys

with open('converting_data.txt', "r", encoding="utf-8") as fin:
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
words = []
exsamples = []
cnt = 0
for i in res:
    curr = f"""['{" ".join(i[0].split()[:-1])}', '{i[1]}'],"""
    if cnt % 2 == 0:
        words.append(curr)
    else:
        exsamples.append(curr)
    cnt += 1
print(*words, sep='\n')
print(*exsamples, sep='\n')