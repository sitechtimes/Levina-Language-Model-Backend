from random import randint

letters = "abcdefghijklmnopqrstuvwxyz"
numbers = "123456789"


def random_alphanumberic(digits):
    string = ""
    for i in range(digits):
        if randint(1, 2) == 1:
            string += letters[randint(0, 25)]
        else:
            string += numbers[randint(0, 8)]
    return string
