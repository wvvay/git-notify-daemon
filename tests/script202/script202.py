import random
def generator():
    rand = random(0,9)
    yield print(rand)

gen = generator()
gen
next(gen)