import random
import string


def generate_password(
    length, use_uppercase=True, use_digits=True, use_special_chars=True
):
    character_set = string.ascii_lowercase
    if use_uppercase:
        character_set += string.ascii_uppercase
    if use_digits:
        character_set += string.digits
    if use_special_chars:
        character_set += string.punctuation

    password = "".join(random.choice(character_set) for _ in range(length))
    return password
