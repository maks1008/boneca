import random

def ragebait():
    """returns a random ragebait message (selected from ragebaitMessages.txt)"""
    with open('botActions/ragebait/ragebaitMessages.txt', encoding='utf-8') as ragebait_file:
        ragebait_list = [line.strip() for line in ragebait_file]
    random.shuffle(ragebait_list)
    return ragebait_list[0]

print(ragebait())