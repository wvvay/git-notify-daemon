import string
import random
alphabet = string.ascii_lowercase
rand_num = random.randint(0, len(alphabet))
print(rand_num + 1, alphabet[rand_num])
