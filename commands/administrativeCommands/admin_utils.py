#RELEVANT FILES
server_permissions_file = 'commands/administrativeCommands/bonecaServerPermissions.txt'
do_not_target_file = 'commands/administrativeCommands/doNotTarget.txt'
glaze_messages_file = 'botActions/glazeMessages.txt'
ragebait_messages_file = 'botActions/ragebaitMessages.txt'
quarantined_messages_file = 'commands/administrativeCommands/quarantinedMessages.txt'

#RELEVANT SETS
server_permissions_set = set()
do_not_target_set = set()

#FILE PROCESSING
def unpack():
    """executed when bot first goes online. unpacks data into abovementioned relevant sets"""
    unpack_txt_files(server_permissions_file, server_permissions_set)
    unpack_txt_files(do_not_target_file, do_not_target_set)

def unpack_txt_files(txt_file, relevant_set):
    """unpacks data from txt_file to relevant_set"""
    with open(txt_file, encoding='utf-8') as processed_txt:
        txt_list = [line.strip() for line in processed_txt]
    for i in txt_list:
        relevant_set.add(i)

def update_txt_files(txt_file, relevant_set):
    """transfers current info in relevant_set to specified txt_file"""
    with open(txt_file, 'w', encoding="utf-8") as new_txt:
        for i in relevant_set:
            new_txt.write("{}\n".format(i))

#BOT FUNCTIONALITY
def introduce(channel_id):
    """adds channel_id to server_permissions_set and bonecaServerPermissions.txt"""
    server_permissions_set.add(channel_id)
    update_txt_files(server_permissions_file, server_permissions_set)

def banish(channel_id):
    """removes channel_id from server_permissions_set and bonecaServerPermissions"""
    server_permissions_set.discard(channel_id)
    update_txt_files(server_permissions_file, server_permissions_set)

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

#GETTERS
def valid_channel(channel_id):
    """checks if channel_id is in server_permissions_set"""
    return channel_id in server_permissions_set

def dnt_user(user):
    """checks if user is in the do not target list"""
    return user in do_not_target_set