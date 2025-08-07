import datetime
import random

thanosrank_dictionary = {}
safe_from_thanos = {}
thanosrank_cooldown = {}

success_messages = ["enjoy thanosrank USER :thumbsup:",
                    "better behave next time USER :police_car:",
                    "i turned USER into dust :thumbsup:",
                    "sent USER to the void :hole:",
                    "made sure USER doesn't bother you again :relieved:",
                    "sorry USER. don't blame me, blame the cornball who called the command"]
nothing_messages = [":yawning_face: nope",
                    "can't really be bothered",
                    "that's a bit too much effort bud",
                    "try again when i care :joy:",
                    "no, i wanna see how this one plays out",
                    "nah, i kinda lost interest halfway into executing it :sleeping:",
                    "you wish :joy:",
                    "i don’t take requests from diddy bluds",
                    "nah i'm saving that for someone who deserves it",
                    "nothing ever happens, and this time's no different"]
fail_messages = ["how about I thanosrank **YOU** instead? :rofl:", 
                 "not happening. I can thanosrank **you** though", 
                 "you're a bit too eager to use that command... think I'm gonna teach **YOU** a lesson :grimacing:",
                 "permission denied :no_entry_sign: you're a better target",
                 "you thought that would work? :sob: how about I give it to **you** instead",
                 "what if... and hear me out... I thanosrank **you**? :smiling_imp:",
                 "you tried to /thanosrank as if you're not built like a victim :skull: i gave it to **you** instead :skull:",
                 "i'm redirecting that one back to you :wave:",
                 "i was gonna do it but then i remembered who asked. enjoy thanosrank buddy :joy_cat:"]

silly_messages = ["what are you doing? you're thanosranked :joy:",
                  "you can't talk for a little while",
                  "don't blame me, i'm just doing my job",
                  "maybe you can log off for a little while and do something productive?",
                  "i don't think you quite understand what being thanosranked means",
                  "honestly, I wanted to let that message through but rules are rules",
                  "what if we run away from the all together?",
                  "doesn't matter how much you talk, no one hears you :joy:",
                  "looks like you're on a break from chatting... enjoy the peace for a little while",
                  "do you still like having me on the server?",
                  "tell you what, you should thanosrank someone when you're free!",
                  "dawg pack it up your messages are NOT gonna go thru"]

def add_to_thanosrank(user, time):
    """adds user to thanosrank"""
    thanosrank_length = random.randint(2, 10)
    time += datetime.timedelta(minutes=thanosrank_length)
    thanosrank_dictionary[user.id] = (time, user.guild)
    safe_from_thanos[user] = (time + datetime.timedelta(minutes=15))

def add_thanos_cooldown(user, time):
    """restricts user from using thanosrank"""
    time += datetime.timedelta(minutes=15)
    thanosrank_cooldown[user] = time

def remove_from_thanosrank(user):
    """removes user from thanosrank"""
    thanosrank_dictionary.pop(user, None)

def remove_from_safety(user):
    """removes user from safe_from_thanos"""
    safe_from_thanos.pop(user, None)

def remove_from_cooldown(user):
    """removes user from thanosrank_cooldown"""
    thanosrank_cooldown.pop(user, None)

def check_thanosrank(user):
    """checks whether or not user is in thanosrank"""
    return user in thanosrank_dictionary

def check_if_safe(user):
    """checks whether user is in safe_from_thanos"""
    return user in safe_from_thanos

def check_cooldown(user):
    """checks whether there is a cooldown applied on the user"""
    return user in thanosrank_cooldown

def check_when_thanosrank_runs_out(user):
    """returns int time indicating when user will be out of thanosrank"""
    time, guild = thanosrank_dictionary[user]
    return time.strftime("%H:%M")

def check_when_safe_from_thanos_runs_out(user):
    """returns int time indicating when user will be allowed to be thanosranked again"""
    return safe_from_thanos[user].strftime("%H:%M")

def check_when_cooldown_runs_out(user):
    """returns int time indicating when user will be allowed to use thanosrank again"""
    return thanosrank_cooldown[user].strftime("%H:%M")

def get_thanosrank_message(mode, user):
    """returns message based on thanosrank success"""
    if mode == 1:
        random.shuffle(success_messages)
        message = success_messages[0].split("USER")
        return "{message[0]}{user.mention}{message[1]}"
    if mode == 2:
        random.shuffle(nothing_messages)
        return nothing_messages[0]
    if mode == 3:
        random.shuffle(fail_messages)
        return fail_messages[0]
    
def silly_thanosrank_message():
    """returns silly message for when someone tried to talk during thanosrank"""
    random.shuffle(silly_messages)
    return silly_messages[0]

def get_all_thanosrank_dictionaries():
    """returns a tuple of all thanosrank_dictionaries"""
    return (thanosrank_dictionary, safe_from_thanos, thanosrank_cooldown)

async def create_thanosrank(server, colour, logs_channel, interaction):
    try:
        #Creates thanosrank
        thanosrank = await server.create_role(
             name="T H A N O S R A N K",
             color=colour,
             hoist=True,
             reason="/thanosrank was used")

        #Moves it up as high as possible in the priority list
        bot_top_role = server.me.top_role
        if bot_top_role.position > 1:
            max_position = bot_top_role.position - 1
            await thanosrank.edit(position=max_position)
    except:
        await logs_channel.send(f"{interaction.user.name} ({interaction.user.id}) ran into difficulties creating T H A N O S R A N K")
        await interaction.followup("Error: Could not create T H A N O S R A N K role. I have notified the developers")