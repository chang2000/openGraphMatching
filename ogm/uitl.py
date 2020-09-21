import os
entries = os.listdir('.')

for e in entries:
    f = open(e, 'r')
    content = f.readline()
    print(content)
    f.close()
