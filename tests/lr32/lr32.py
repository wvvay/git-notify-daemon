import random
import string

random_string = ''.join(random.choices(string.ascii_uppercase, k=10))
print("Случайная строка:", random_string)


