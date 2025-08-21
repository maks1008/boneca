#IMPORTS
import asyncio
import discord
import datetime
from math import ceil
import os
import random
from discord.ext import commands

import botActions.messageReactions as messageReactions
import commands.administrativeCommands.admin_utils as admin_utils
import commands.functionalityCommands.thanosrank as thanosrank





#ESTABLISHES PERMISSIONS
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(command_prefix="!", intents=intents)





#GLOBAL VARIABLES
BOT_TOKEN = os.getenv("BONECA_TOKEN")
if BOT_TOKEN is None:
    raise ValueError("BONECA_TOKEN not found in environmental variables")
TESTING_SERVER_ID = discord.Object(id=1368129546578300978)
LOGS_CHANNEL_ID = 1402951184385441804
COOLDOWN = 5

#EVENT FUNCTIONS
@client.event
async def on_ready():
    logs_channel = await client.fetch_channel(LOGS_CHANNEL_ID)
    unpack() #loads data from txt files into relevant sets
    try:
        #await client.tree.sync()
        await client.tree.sync(guild=TESTING_SERVER_ID)
    except Exception as e:
        await logs_channel.send("SYNCING ERROR: {}".format(e))
    client.loop.create_task(thanosrank_service())
    await logs_channel.send(f"{client.user} is up and running!")

@client.event
async def on_message(message):
    """MESSAGE REACTIONS"""
    channel_id = message.channel.id

    #IGNORES THE FOLLOWING MESSAGES
    if check_thanosrank(message.author.id):
        await message.delete()
        await message.author.send(thanosrank.silly_thanosrank_message())
        return
    if message.author == client.user:
        return
    if get_dnt_user(message.author.id):
        return
    if not admin_utils.get_valid_channel(channel_id):
        return
        
    #RUNS TRIGGER WORD DETECTOR
    trigger = messageReactions.triggers_detected(message.content)
    if trigger is not False:
        async with message.channel.typing():
            await asyncio.sleep(admin_utils.typing_speed(trigger))
            await message.channel.send(messageReactions.trigger_message(trigger))
        return
        
    #GENERATES A MESSAGE RESPONSE (glazing/ragebait)
    global last_message_sent
    if datetime.datetime.now() - last_message_sent < datetime.timedelta(minutes=COOLDOWN):
        return
    response_frequency = admin_utils.get_channel_message_frequency(channel_id)
    action_value = random.randrange(1, 2 * response_frequency + 1)
    if action_value == 1:
        glaze = messageReactions.message_response("GLAZING")
        async with message.channel.typing():
            await asyncio.sleep(admin_utils.typing_speed(glaze))
            await message.channel.send(glaze)
            last_message_sent = datetime.datetime.now()
        return
    elif action_value == 2:
        ragebait = messageReactions.message_response("RAGEBAITING")
        async with message.channel.typing():
            await asyncio.sleep(admin_utils.typing_speed(ragebait))
            await message.channel.send(ragebait)
            last_message_sent = datetime.datetime.now()
        return

@client.event
async def on_guild_join(self, guild):
    """When Boneca joins the server for the first time"""
    welcome = f"Thanks for inviting me to **{guild.name}**! Use /help to get started."
    for channel in guild.text_channels:
        if "welcome" in channel.name.lower() or "general" in channel.name.lower():
            await channel.send(welcome)
            return
            
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        await guild.system_channel.send(welcome)
        return





#SETTINGS SLASH COMMANDS
@client.tree.command(name="introduce", description="Give Boneca permission to interact with current channel")
async def introduce_boneca(interaction: discord.Interaction):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("I understand attempting to use /notme or /banish when you've been thanosranked, but what are you trying to achieve here?")
        return
    if interaction.user.guild_permissions.administrator:
        channel = (interaction.channel)
        if admin_utils.get_valid_channel(channel.id):
            await interaction.response.send_message(f"I already have permissions to interact with {interaction.channel.mention}!", ephemeral=True)
            return
        else:
            await interaction.response.defer()
            await admin_utils.introduce(channel)
            await interaction.followup.send(f"You have given me permission to interact with {interaction.channel.mention}!")
            return
    else:
        await interaction.response.send_message("This command may only be used by admins of this server.", ephemeral=True)

@client.tree.command(name="banish", description="Remove Boneca's permission to interact with current channel")
async def banish_boneca(interaction: discord.Interaction):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("Nice try but I don't take orders from a dude with a purple T H A N O S R A N K tag :joy::thumbsup:")
        return
    if interaction.user.guild_permissions.administrator:
        channel = (interaction.channel)
        if admin_utils.get_valid_channel(channel.id):
            admin_utils.banish(channel.id)
            await interaction.response.send_message(f"Aw man :frowning2: you've taken away my permission to interact with {interaction.channel.mention} :frowning2:")
        else:
            await interaction.response.send_message("I can't talk here anyway :joy_cat::pray:", ephemeral=True)
    else:
        await interaction.response.send_message("This command may only be used by admins of this server.", ephemeral=True)

@client.tree.command(name="frequency", description="Override Boneca's default response rate")
@discord.app_commands.describe(x="New rate")
async def frequency_boneca(interaction: discord.Integration, x: int):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("Frequency doesn't effect your T H A N O S R A N K status :joy: why bother trying to use it?")
        return
    if not admin_utils.get_valid_channel(interaction.channel.id):
        await interaction.response.send_message("I can't talk here. Use /introduce to give me permissions to interact with this channel.", ephemeral=True)
        return
    if interaction.user.guild_permissions.administrator:
        admin_utils.set_channel_message_frequency(interaction.channel.id, x)
        await interaction.response.send_message(f"I will now respond once every {x} messages")
    else:
        await interaction.response.send_message("This command may only be used by admins of this server.", ephemeral=True)

@client.tree.command(name="help", description="Learn about Boneca's functionality")
async def help_boneca(interaction: discord.Integration):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("Trust me, there's no way to escape T H A N O S R A N K.")
        return
    file = discord.File("boneca010.png", filename="boneca010.png")

    boneca_overview = discord.Embed(title="", 
                                  color=discord.Color.green())
    boneca_overview.set_image(url="attachment://boneca010.png")
    
    getting_started = discord.Embed(title="TO GET STARTED :technologist:",
                                  description="Use /integrate to allow me to interact with the current channel. From there, carry on with your conversation and enjoy the ride :smiling_imp: I will aim to respond either once every 15 messages, or 5 times per day (choosing the lower rate).",
                                  color=discord.Color.green())
    
    settings = discord.Embed(title="SETTINGS COMMANDS :gear:",
                             color=discord.Color.green())
    settings.add_field(name=":wave: /introduce", 
                       value="Give Boneca permission to interact with current channel.", 
                       inline=False)
    settings.add_field(name=":door: /banish", 
                       value="Remove Boneca's permission to interact with current channel.", 
                       inline=False)
    settings.add_field(name=":clock8: /frequency", 
                       value="Override Boneca's default response rate. Note: Boneca runs on RNG. Setting frequency to x will result in a 1/x chance of response.", 
                       inline=False)
    settings.add_field(name=":x: /notme", 
                       value="Toggle Boneca's permission to interact with you.", 
                       inline=False)
    settings.add_field(name=":thumbsdown: /report", 
                       value="Flag Boneca's last message as inappropriate (or unfunny)", 
                       inline=False)
    settings.add_field(name=":bulb: /suggest", 
                       value="Suggest features for future Boneca updates", 
                       inline=False)

    ragebait_glazing_commands = discord.Embed(title="RAGEBAIT + GLAZING COMMANDS :video_game:",
                                              color=discord.Color.green())
    ragebait_glazing_commands.add_field(name=":mag_right: /factcheck",
                                        value="Fact check the previous statement",
                                        inline=False)
    ragebait_glazing_commands.add_field(name=":troll: /thanosrank",
                                        value="Vaporize another user",
                                        inline=False)
    ragebait_glazing_commands.add_field(name="",
                                        value=":bangbang:**MORE COMING SOON**:bangbang:",
                                        inline=False)
    
    passive_activity = discord.Embed(title=":eyes: PASSIVE ACTIVITY",
                               color=discord.Color.green())
    passive_activity.add_field(name=":cold_face: Ragebaiting + Glazing",
                               value="Boneca uses RNG to deliver ragebait and glazing messages throughout the day",
                               inline=False)
    passive_activity.add_field(name=":sleeping_accommodation: Goodnight Messages",
                               value="Try saying goodnight to Boneca!",
                               inline=False)
    passive_activity.add_field(name=":bangbang:**AND MORE**:bangbang:",
                               value="Revealing too much would spoil the fun :wink:",
                               inline=False)

    await interaction.response.send_message(embeds=[boneca_overview, getting_started, settings, ragebait_glazing_commands, passive_activity], file=file)

@client.tree.command(name="notme", description="Toggle Boneca's permission to interact with you")
async def notme_boneca(interaction: discord.Integration):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("Try again when you're not thanosranked.")
        return
    user = interaction.user.id
    admin_utils.not_me(user)
    if admin_utils.get_dnt_user(user):
        await interaction.response.send_message("You've been added to Boneca's safe list. Boneca will never target you.", ephemeral=True)
    elif not admin_utils.get_dnt_user(user):
        await interaction.response.send_message("You've been removed from Boneca's safe list. Boneca will keep an eye out on you!", ephemeral=True)

@client.tree.command(name="report", description="Flag Boneca's last message as inappropriate")
async def report_boneca(interaction: discord.Integration):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("Don't report me bud, it wasn't my choice to T H A N O S R A N K you")
        return
    channel = interaction.channel
    apologies = ["I'm sorry :worried: I took that too far... I've removed that prompt from my database.",
                 "I'm sorry :worried: I took that too far... I have asked the devs to review this one ASAP.",
                 "I can't figure out what I did wrong :disappointed: Please get in touch with @datkid10021 ASAP."]
    
    async for message in channel.history(limit=20):
        if message.author == client.user and message.content not in apologies:

            #FLICKS A DM TO THE REPORT CHANNEL OF RBBT
            report_channel = await client.fetch_channel(1402235942131208244)
            await report_channel.send(f"**{interaction.user.name} ({interaction.user.id}) used /report:** {message.content}")

            #REMOVES MESSAGE
            report_status = admin_utils.report(message.content)
            await message.delete()
            if report_status:
                await interaction.response.send_message(apologies[0])
            else:
                await interaction.response.send_message(apologies[1])
            return
    await interaction.channel.send(apologies[2])

@client.tree.command(name="suggest", description="Suggest features for future Boneca updates")
async def suggest_boneca(interaction: discord.Integration, suggestion: str):
    suggest_channel = await client.fetch_channel(1402236026084397138)
    await suggest_channel.send(f"**{interaction.user.name} ({interaction.user.id}) used /suggest:** {suggestion}")
    await interaction.response.send_message("Thanks! I'll send you an update if the devs start working on this.", ephemeral=True)

#FUNCTIONALITY SLASH COMMANDS
@client.tree.command(name="factcheck", description="Fact check the previous statement")
async def boneca_factcheck(interaction: discord.Integration):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("Claim: You've got T H A N O S R A N K\nFact Check: True :thumbsup:")
        return
    truth = random.randint(0,1)
    if truth == 0: 
        await interaction.response.send_message("https://tenor.com/view/fact-check-kellanrockssoccer-gif-2569170256995872124")
        return
    if truth == 1:
        await interaction.response.send_message("https://tenor.com/view/memes-gif-9980668056796018353")
        return

@client.tree.command(name="thanosrank", description="Vaporize another user")
@discord.app_commands.describe(target="Tag the user you'd like to thanosrank")
async def boneca_thanosrank(interaction: discord.Integration, target: discord.Member):
    #SETUP
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("You trynna drag others down with you?")
        return

    await interaction.response.defer()
    server = interaction.guild
    logs_channel = await client.fetch_channel(LOGS_CHANNEL_ID)
    thanosrank_role = discord.utils.get(server.roles, name="T H A N O S R A N K")
    now = datetime.datetime.now()
    if thanosrank_role is None:
        thanosrank_role = await thanosrank.create_thanosrank(server, discord.Color.dark_purple(), logs_channel, interaction)

    #ELIGIBILITY CHECKS
    attacker = interaction.user
    if admin_utils.get_dnt_user(attacker.id):
        await interaction.followup.send("Use /notme to gain access to Boneca's functionality")
        return
        
    if thanosrank.check_cooldown(attacker.id):
        await interaction.followup.send(f"You can't use /thanosrank until {thanosrank.check_when_cooldown_runs_out(attacker.id)}")
        return
    
    if admin_utils.get_dnt_user(target.id):
        await interaction.followup.send("You cannot use /thanosrank on the selected user.")
        return
    if thanosrank.check_if_safe(target.id):
        await interaction.followup.send("Selected user is safe from /thanosrank.")
        return

    #/THANOSRANK STARTS HERE
    thanosrank.add_thanos_cooldown(interaction.user, now)
    fate_decider = random.randint(1,3) #1 = follow thru, 2 = nothing happens, 3 = betray

    if fate_decider == 2: #nothing happens
        await interaction.followup.send(thanosrank.get_thanosrank_message(fate_decider, target))
        return
    
    if fate_decider == 3: #thanosrank betrays
        target = interaction.user
    
    thanosrank.add_to_thanosrank(target, now)
    await target.add_roles(thanosrank_role, reason="Thanosranked")

    await target.send(f"You've been thanosranked until {thanosrank.check_when_thanosrank_runs_out(target.id)} :thumbsup:")
    await interaction.followup.send(thanosrank.get_thanosrank_message(fate_decider, target))

async def thanosrank_service():
    await client.wait_until_ready()
    while not client.is_closed():
        now = datetime.datetime.now()
        try:
            thanosrank_dictionary, safe_from_thanos, thanosrank_cooldown = thanosrank.get_all_thanosrank_dictionaries()
            remove_from_thanosrank = []
            remove_from_safety = []
            remove_from_cooldown = []
            for i in thanosrank_dictionary:
                time, guild = thanosrank_dictionary[i]
                if now >= time:
                    thanosrank_role = discord.utils.get(guild.roles, name="T H A N O S R A N K")
                    member = await guild.fetch_member(i)
                    await member.remove_roles(thanosrank_role, reason="Free from T H A N O S R A N K")
                    remove_from_thanosrank.append(i)
            for i in safe_from_thanos:
                if now >= safe_from_thanos[i]:
                    remove_from_safety.append(i)
            for i in thanosrank_cooldown:
                if now >= thanosrank_cooldown[i]:
                    remove_from_cooldown.append(i)

            for i in remove_from_thanosrank:
                thanosrank.remove_from_thanosrank(i)
            for i in remove_from_safety:
                thanosrank.remove_from_safety(i)
            for i in remove_from_cooldown:
                thanosrank.remove_from_cooldown(i)
            
        except Exception as e:
            print(e)
            return
            #logs_channel = await client.fetch_channel(LOGS_IG)
            #await logs_channel.send(f"ERROR: thanosrank_service() IS BUSTED!: {e}")
        await asyncio.sleep(60)

#MANDATORY FOR BOT TO RUN
client.run(BOT_TOKEN)




















"""THE FOLLOWING SECTION CONTAINS VARIOUS HELPER FUNCTIONS ROUGHLY IN THIS ORDER:
    1. commands/administrativeCommands/admin_utils.py
    2. commands/functionalityCommands/thanosrank.py
    """

TARGET_MESSAGES_PER_DAY = 5 #how many messages boneca will send daily

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
    """executed when bot first goes online. unpacks data into relevant sets"""
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


#SLASH COMMANDS HELPER FUNCTIONS
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
    if boneca_message_frequency < 15:
        allowed_channels[channel.id] = 15
    else:
        allowed_channels[channel.id] = boneca_message_frequency

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
                  "what if we run away from all of this together?",
                  "doesn't matter how much you talk, no one hears you :joy:",
                  "looks like you're on a break from chatting... enjoy the peace for a little while",
                  "do you still like having me on the server?",
                  "tell you what, you should thanosrank someone when you're free!",
                  "dawg pack it up your messages are NOT gonna go thru",
                  "seriously, stop talking. just sit this out.",
                  "i hawk tuah on you! :joy: :sweat_drops:",
                  "send 6-7 messages and i might change my mind",
                  "you can't talk until you've done your time",
                  "you're starting to annoy me :anger:",
                  "fun fact: if an admin removes the T H A N O S R A N K role from you, that won't effect my behaviour at all. In fact, that will cause a serious error in my code and you'll be T H A N O S R A N K E D until the developers reboot me :skull:",
                  "fun fact: no one's ever given you hawk tuah :joy:",
                  "fun fact: _ (make up your own fun fact)",
                  "fun fact: currently i have a list of 100 ragebait prompts and a list of 100 glazing prompts. i use rng to decide which prompt to use. in v1.0.0, i will use a LLM to generate custom ragebait and glazing based on the context of the conversation.",
                  "fun fact: Maksim Studios are not working on a $Boneca crypto coin yet. Is this something we should look into?",
                  "blah blah blah",
                  "did the crime? time to do the time",
                  "you're in the thick of it, everybody knows, they know you where it snows, you skied in and they froze",
                  "fun fact: in the MCU thanos snaps half the population of the universe out of existence indefinetly. here at Maksim Studios, i've been designed such that only 1 person gets snapped out of existence, and they only dissapear for 2-10 minutes. Maksim's generous, eh?"
                  "at the very least no one will be able to target you for 15 minutes after you're out of here",
                  "fun fact: if you smash your face into the wall, you will have to pay for the following: wall reparation, ambulance trip, face surgery. and guess what? you STILL won't be able to escape thanosrank",
                  "don't view this as a punishment. take this time to scroll thru you favourite short form content platform! thanosrank doesn't last long enough for anything else.",
                  "fun fact: boneca isn't a ragebait bot. behind the screen, boneca is actually an employee of Maksim Studios hired to ragebait and glaze people. i'm currently learning english so i apologize if some of the stuff i say doesn't make sense. seriously - there's no bad blood. i'm just paid to thanosrank you and to roast you."]

def add_to_thanosrank(user, time):
    """adds user to thanosrank"""
    thanosrank_length = random.randint(2, 10)
    time += datetime.timedelta(minutes=thanosrank_length)
    thanosrank_dictionary[user.id] = (time, user.guild)
    safe_from_thanos[user.id] = (time + datetime.timedelta(hours=2))

def add_thanos_cooldown(user, time):
    """restricts user from using thanosrank"""
    time += datetime.timedelta(minutes=15)
    thanosrank_cooldown[user.id] = time

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
        return f"{message[0]}{user.mention}{message[1]}"
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