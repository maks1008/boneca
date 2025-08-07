from math import ceil
import random

TARGET_MESSAGES_PER_DAY = 8 #how many messages boneca will send daily

#RELEVANT FILES
server_permissions_file = 'commands/administrativeCommands/bonecaServerPermissions.txt'
do_not_target_file = 'commands/administrativeCommands/doNotTarget.txt'
glaze_messages_file = 'botActions/glazeMessages.txt'
ragebait_messages_file = 'botActions/ragebaitMessages.txt'
quarantined_messages_file = 'commands/administrativeCommands/quarantinedMessages.txt'

#RELEVANT SETS
server_permissions_set = set()
allowed_channels = {}
do_not_target_set = set()

#FILE PROCESSING
def unpack():
    """executed when bot first goes online. unpacks data into abovementioned relevant sets"""
    unpack_txt_files_into_dictionary(server_permissions_file, allowed_channels)
    unpack_txt_files(do_not_target_file, do_not_target_set)

def unpack_txt_files(txt_file, relevant_set):
    """unpacks data from txt_file to relevant_set"""
    with open(txt_file, encoding='utf-8') as processed_txt:
        txt_list = [line.strip() for line in processed_txt]
    for i in txt_list:
        relevant_set.add(i)

def unpack_txt_files_into_dictionary(txt_file, dictionary):
    """unpacks data from txt_file to dictionary"""
    with open(txt_file, encoding='utf-8') as processed_txt:
        txt_list = [line.strip() for line in processed_txt]
    for line in txt_list:
        channel_id, message_frequency = line.split(" ")
        allowed_channels[channel_id] = int(message_frequency)


def update_txt_files(txt_file, relevant_set):
    """transfers current info in relevant_set to specified txt_file"""
    with open(txt_file, 'w', encoding="utf-8") as new_txt:
        for i in relevant_set:
            new_txt.write("{}\n".format(i))

def update_txt_files_from_dictionary(txt_file, dictionary):
    """transfers info from given dictionary to given txt_file"""
    with open(txt_file, 'w', encoding="utf-8") as new_txt:
        for channel in dictionary:
            new_txt.write("{} {}\n".format(channel, dictionary[channel]))


#SLASH COMMANDS
async def introduce(channel):
    """adds channel_id to server_permissions_set and bonecaServerPermissions.txt"""
    allowed_channels[str(channel.id)] = 0
    await frequency_gauge(channel)
    update_txt_files_from_dictionary(server_permissions_file, allowed_channels)


def banish(channel_id):
    """removes channel_id from server_permissions_set and bonecaServerPermissions"""
    allowed_channels.pop(channel_id, None)
    update_txt_files_from_dictionary(server_permissions_file, allowed_channels)

def not_me(user):
    """adds/removes user in do_not_target_set and do_not_target_file"""
    if user in do_not_target_set:
        do_not_target_set.discard(user)
    else:
        do_not_target_set.add(user)
    update_txt_files(do_not_target_file, do_not_target_set)

def report(message):
    """#1 - quarantines message 
    #2 - removes message from glaze/ragebait pool
    #3 - returns True if message was wiped from txt files, False is message is hard coded elsewhere"""
    with open(quarantined_messages_file, 'a', encoding='utf-8') as quarantined_messages:
        quarantined_messages.write("{}\n".format(message))

    with open(ragebait_messages_file, encoding='utf-8') as ragebait_prompt_file:
            ragebait_prompt_list = [line.strip() for line in ragebait_prompt_file]
    if message in ragebait_prompt_list:
        ragebait_prompt_list.remove(message)
        with open(ragebait_messages_file, 'w', encoding='utf-8') as ragebait_prompt_file:
            for i in ragebait_prompt_list:
                 ragebait_prompt_file.write('{}\n'.format(i))     
        return True

    with open(glaze_messages_file, encoding='utf-8') as glaze_prompt_file:
            glaze_prompt_list = [line.strip() for line in glaze_prompt_file]
    if message in glaze_prompt_list:
        glaze_prompt_list.remove(message)
        with open(glaze_messages_file, 'w', encoding='utf-8') as glaze_prompt_file:
            for i in glaze_prompt_list:
                 glaze_prompt_file.write('{}\n'.format(i))     
        return True
    
    return False

#HELPER COMMANDS
async def frequency_gauge(channel):
    """Returns the frequency of Boneca's messages in given channel"""
    messages_per_day = [0 for i in range(10)]
    latest_date = None
    day = -1
    async for message in channel.history(limit=None, oldest_first=False):
        message_date = message.created_at.date()
        if day >= 9:
            break
        elif latest_date != message_date or latest_date == None:
            latest_date = message_date
            day += 1
            messages_per_day[day] += 1
        elif latest_date == message_date:
            messages_per_day[day] += 1
            
    average_messages_per_day = ceil(sum(messages_per_day)/len(messages_per_day))
    boneca_message_frequency = average_messages_per_day // TARGET_MESSAGES_PER_DAY
    print(f"messages_per_day: {messages_per_day}\n average_messages_per_day: {average_messages_per_day}\nboneca_message_frequency: {boneca_message_frequency}")
    if boneca_message_frequency < 8:
        allowed_channels[str(channel.id)] = 8
    else:
        allowed_channels[str(channel.id)] = boneca_message_frequency

def typing_speed(string):
    """returns an integer representing the amount of seconds Boneca should spend typing that message"""
    funny_prompts = [":joy:", ":rofl:", "facts", "real"] #funny prompts
    for i in funny_prompts:
        if i in string.lower() and len(string) < 15:
            return 30
    words_per_minute = random.randint(55, 75)
    words = len(string.split(" "))
    return (words * 60) / (words_per_minute)

#GETTERS
def get_valid_channel(channel_id):
    """checks if channel_id is in server_permissions_set"""
    return channel_id in allowed_channels

def get_channel_list():
    """returns list of all channels where Boneca is allowed to talk"""
    channels = []
    for i in allowed_channels:
        channels.append(i)
    return channels

def get_channel_message_frequency(channel_id):
    """return's boneca's current message frequency on specified channel"""
    return allowed_channels[channel_id]

def get_dnt_user(user):
    """checks if user is in the do not target list"""
    return user in do_not_target_set

#SETTERS
def set_channel_message_frequency(channel_id, x):
    """sets channel_id message frequency to x"""
    allowed_channels[channel_id] = x
    update_txt_files_from_dictionary(server_permissions_file, allowed_channels)