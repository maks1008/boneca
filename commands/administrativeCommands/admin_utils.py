server_permissions_file = 'commands/administrativeCommands/bonecaServerPermissions.txt'
accepted_channel_id = set()

do_not_target_file = 'commands/administrativeCommands/doNotTarget.txt'
do_not_target_set = set()

glaze_messages_file = 'botActions/glazeMessages.txt'
ragebait_messages_file = 'botActions/ragebaitMessages.txt'
quarantined_messages_file = 'commands/administrativeCommands/quarantinedMessages.txt'


def unpack():
    """converts all channel ids from channelID.txt into the accepted_channel_id set"""
    with open(server_permissions_file, encoding='utf-8') as channelID_file:
        channelID_list = [line.strip() for line in channelID_file]
    for i in channelID_list:
        accepted_channel_id.add(i)

def unpack_do_not_target():
    """converts all channel ids from doNotTarget.txt into the accepted_channel_id set"""
    with open(do_not_target_file, encoding='utf-8') as dnt_file:
        dnt_list = [line.strip() for line in dnt_file]
    for i in dnt_list:
        do_not_target_set.add(i) 

def update_server_permissions():
    """updates bonecaServerPermissions.txt to whats currently in accepted_channel_id"""
    with open(server_permissions_file, 'w', encoding='utf-8') as channelID_file:
        for i in accepted_channel_id:
            channelID_file.write("{}\n".format(i))

def update_doNotTargetTXT():
    with open(do_not_target_file, 'w', encoding='utf-8') as dnt_file:
        for i in do_not_target_set:
            dnt_file.write("{}\n".format(i))

def introduce(channel_id):
    """adds channel_id to accepted_channel_id and bonecaServerPermissions.txt"""
    accepted_channel_id.add(channel_id)
    update_server_permissions()

def banish(channel_id):
    """removes channel_id from accepted_channel_id and bonecaServerPermissions"""
    accepted_channel_id.discard(channel_id)
    update_server_permissions()

def accepted_channel(channel_id):
    """checks if channel_id is an accepted channel"""
    return channel_id in accepted_channel_id

def dnt_user(user):
    """checks if user is in the do_not_target_set"""
    return user in do_not_target_set

def report(message):
    """#1 - quarantines message 
    #2 - removes message from glaze/ragebait pool and send True if execution successful"""
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

def not_me1(user):
    """adds user to do_not_target_set and do_not_target_file"""
    do_not_target_set.add(user)
    update_doNotTargetTXT()

def not_me2(user):
    """removes user from do_not_target_set and do_not_target_file"""
    do_not_target_set.discard(user)
    update_doNotTargetTXT()