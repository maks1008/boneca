import random

with open('botActions/ragebait/ragebaitMessages.txt') as ragebait_file:
    ragebait = [line.strip() for line in ragebait_file]

random.shuffle(ragebait)

print(ragebait)