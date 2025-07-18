import random

def glazing():
    """returns a random glazing message (selected from glazeMessages.txt)"""
    with open('botActions/glaze/glazeMessages.txt') as glaze_file:
        glaze_list = [line.strip() for line in glaze_file]
    random.shuffle(glaze_list)
    return glaze_list[0]