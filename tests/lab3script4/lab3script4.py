import random

def is_palindrome(s):
    return s[::] == s[::-1]

temp_list = [random.randint(1, 1000) for _ in range(10)]
print('Сгенерированный список: ', *temp_list)
for j in temp_list:
    if is_palindrome(j):
        print('{} - палиндром'.format(j))