import random
import string


def generate_password(length=16, chars=string.ascii_letters):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))


def get_rand(criteria):
    summary_probability = sum(i[-1] for i in criteria)
    val = random.uniform(0, summary_probability)
    prev = 0
    for i in criteria:
        if prev + i[-1] >= val:
            return i[0]
        prev += i[-1]
