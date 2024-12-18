import random

count = None

with open('counter.txt', 'r') as f:
    count = int(f.read())

with open('numbers.txt', 'w') as f:
    for i in range(count):
        f.write(str(random.randint(0, 100)))
        f.write('\n')