import random



### TRIGGER DETECTOR ###
trigger_words = ['huh', 'lmfao']

def triggers_detected(message):
    """returns trigger words which have been detected"""
    filtered_message = ""
    for i in message:
        if i.isalpha():
            filtered_message += i
    for i in trigger_words:
        if i in filtered_message:
            return i
    return False

def trigger_message(trigger_word):
    if trigger_word == 'huh':
        return "dw"
    if trigger_word == 'lmfao':
        return "dunno man it really isnt THAT funny :wilted_rose::broken_heart:"



### MESSAGE RESPONSE ###
def message_response(type):
    """returns prompt depending on the specified type, where type = GLAZING or RAGEBAITING"""
    if type == "GLAZING":
        text_file = 'botActions/glazeMessages.txt'
    elif type == "RAGEBAITING":
        text_file = 'botActions/ragebaitMessages.txt'
    else:
        raise ValueError("message_response() recieved input != 'GLAZING' or != 'RAGEBAITING'")
    with open(text_file, encoding='utf-8') as prompt_file:
            prompt_list = [line.strip() for line in prompt_file]    
    random.shuffle(prompt_list)
    return prompt_list[0]