import random, time, os
chars = '01'
GREEN = '\033[92m'
RESET = '\033[0m'
while True:
    line = ''.join(random.choice(chars)for _ in range(80))
    print(GREEN + line + RESET)
    time.sleep(0.1)