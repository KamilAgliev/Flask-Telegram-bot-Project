import sys

mas = []
for line in sys.stdin:
    line = line.strip()
    d = eval(line)
    mas.append([d['eng'], d['translate']])
for i in mas:
    print(f"""['{i[0]}', '{i[1]}'],""")