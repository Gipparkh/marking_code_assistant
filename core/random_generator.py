import random
import string


def generate_random_string(length: int) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))