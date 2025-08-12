import asyncio
import botActions.messageReactions as messageReactions
import commands.administrativeCommands.admin_utils as admin_utils
import commands.administrativeCommands.memorial as memorial
import commands.functionalityCommands.thanosrank as thanosrank
import discord
import datetime
import os
import random
from discord.ext import commands


RBBT_SERVER_ID = discord.Object(id=1368129546578300978) #TESTING SERVER ID
KAWAII_SERVER_ID = discord.Object(id=440657990287360001)
PENTHOUSE_ID = 510993237926871054
LOGS_IG = 1402951184385441804
last_message_sent = datetime.datetime.now()
cool_down = 0

BOT_TOKEN = os.getenv("BONECA_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("BONECA_TOKEN not found in environmental variables")

class Client(commands.Bot):
    async def on_ready(self):
        """AS SOON AS BOT GOES ONLINE"""
        admin_utils.unpack()
        last_message_sent = datetime.datetime.now()

        try: #FORCES BOT TO SYNC SLASH COMMANDS
            await self.tree.sync()
            #synced = await self.tree.sync(guild=RBBT_SERVER_ID)
            #print(f"{len(synced)} commands synced successfully.")
        except Exception as e:
            logs_channel = await client.fetch_channel(1402951184385441804)
            await logs_channel.send("SYNCING ERROR: {}".format(e))
        #client.loop.create_task(memorial_checker())
        client.loop.create_task(thanosrank_service())
        print(f"{self.user} is up and running!")
    
    async def on_message(self, message):
        """MESSAGE REACTIONS"""
        channel_id = str(message.channel.id)

        #IGNORES THE FOLLOWING MESSAGES
        if thanosrank.check_thanosrank(message.author.id):
            await message.delete()
            await message.author.send(thanosrank.silly_thanosrank_message())
            return
        if message.author == self.user:
            return
        if admin_utils.get_dnt_user(str(message.author.id)):
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
        if datetime.datetime.now() - last_message_sent < datetime.timedelta(minutes=cool_down):
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


#THE FOLLOWING SECTION INITIALIZES AND EXECUTES BOT'S SLASH COMMANDS
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents) #command prefix is arbitrary, discord enforces slash commands

#SETTINGS SLASH COMMANDS
@client.tree.command(name="introduce", description="Give Boneca permission to interact with current channel")
async def introduce_boneca(interaction: discord.Interaction):
    if thanosrank.check_thanosrank(interaction.user.id):
        await interaction.response.send_message("I understand attempting to use /notme or /banish when you've been thanosranked, but what are you trying to achieve here?")
        return
    if interaction.user.guild_permissions.administrator:
        channel = (interaction.channel)
        channel_id = str(channel.id)
        if admin_utils.get_valid_channel(channel_id):
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
        channel_id = str(channel.id)
        if admin_utils.get_valid_channel(channel_id):
            admin_utils.banish(channel_id)
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
    if not admin_utils.get_valid_channel(str(interaction.channel.id)):
        await interaction.response.send_message("I can't talk here. Use /introduce to give me permissions to interact with this channel.", ephemeral=True)
        return
    if interaction.user.guild_permissions.administrator:
        admin_utils.set_channel_message_frequency(str(interaction.channel.id), x)
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
    user = str(interaction.user.id)
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
    if thanosrank.check_thanosrank(interaction.user):
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
    if thanosrank.check_thanosrank(interaction.user):
        await interaction.response.send_message("You trynna drag others down with you?")
        return

    await interaction.response.defer()
    server = interaction.guild
    logs_channel = await client.fetch_channel(LOGS_IG)
    thanosrank_role = discord.utils.get(server.roles, name="T H A N O S R A N K")
    now = datetime.datetime.now()
    if thanosrank_role is None:
        thanosrank_role = await thanosrank.create_thanosrank(server, discord.Color.dark_purple(), logs_channel, interaction)

    #ELIGIBILITY CHECKS
    attacker = interaction.user
    if admin_utils.get_dnt_user(str(attacker.id)):
        await interaction.followup.send("Use /notme to gain access to Boneca's functionality")
        return
        
    if thanosrank.check_cooldown(attacker.id):
        await interaction.followup.send(f"You can't use /thanosrank until {thanosrank.check_when_cooldown_runs_out(attacker.id)}")
        return
    
    if admin_utils.get_dnt_user(str(target.id)):
        await interaction.followup.send("You cannot use /thanosrank on the selected user.")
        return
    if thanosrank.check_if_safe(target.id):
        await interaction.followup.send("Selected user is safe from /thanosrank.")
        return

    #/THANOSRANK STARTS HERE
    thanosrank.add_thanos_cooldown(interaction.user.id, now)
    fate_decider = random.randint(1,3) #1 = follow thru, 2 = nothing happens, 3 = betray

    if fate_decider == 2: #nothing happens
        await interaction.followup.send(thanosrank.get_thanosrank_message(fate_decider, target))
        return
    
    if fate_decider == 3: #thanosrank betrays
        target = interaction.user
    
    await target.add_roles(thanosrank_role, reason="Thanosranked")
    thanosrank.add_to_thanosrank(target, now)

    await target.send(f"You've been thanosranked until {thanosrank.check_when_thanosrank_runs_out(target.id)} :thumbsup:")
    await interaction.followup.send(thanosrank.get_thanosrank_message(fate_decider, target))


async def memorial_checker():
    await client.wait_until_ready()
    penthouse = await client.fetch_channel(PENTHOUSE_ID)
    while not client.is_closed():
        now = datetime.datetime.now()
        if 17 <= now.hour < 24:
            try:
                event, message = memorial.memorial()
                if event == True:
                    await penthouse.send(message)
            except Exception as e:
                    testing_channel = await client.fetch_channel(1394633667351150682)
                    await testing_channel.send(f"**EMERGENCY!** memorial_checker() IS BUSTED!: {e}")
        await asyncio.sleep(1200)

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

            for time, guild in remove_from_thanosrank:
                thanosrank_role = discord.utils.get(guild.roles, name="T H A N O S R A N K")
                member = await guild.fetch_member(i)
                await member.remove_roles(thanosrank_role, reason="Free from T H A N O S R A N K")
            
        except Exception as e:
            print(e)
            return
            #logs_channel = await client.fetch_channel(LOGS_IG)
            #await logs_channel.send(f"ERROR: thanosrank_service() IS BUSTED!: {e}")
        await asyncio.sleep(60)

#MANDATORY FOR BOT TO RUN
client.run(BOT_TOKEN)