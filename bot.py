import asyncio
import botActions.messageReactions as messageReactions
import commands.administrativeCommands.admin_utils as admin_utils
import commands.administrativeCommands.memorial as memorial
import discord
import datetime
import os
import random
from discord.ext import commands


RBBT_SERVER_ID = discord.Object(id=1368129546578300978) #TESTING SERVER ID
KAWAII_SERVER_ID = discord.Object(id=440657990287360001)
PENTHOUSE_ID = 510993237926871054

BOT_TOKEN = os.getenv("BONECA_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("BONECA_TOKEN not found in environmental variables")

class Client(commands.Bot):
    async def on_ready(self):
        """AS SOON AS BOT GOES ONLINE"""
        admin_utils.unpack()

        try: #FORCES BOT TO SYNC SLASH COMMANDS
            synced = await self.tree.sync(guild=RBBT_SERVER_ID)
            print(f"{len(synced)} commands synced successfully.")
        except Exception as e:
            print("SYNCING ERROR: {}".format(e))
        client.loop.create_task(memorial_checker())
        print(f"{self.user} is up and running!")
    
    async def on_message(self, message):
        """MESSAGE REACTIONS"""
        channel_id = str(message.channel.id)

        #IGNORES THE FOLLOWING MESSAGES
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
        response_frequency = admin_utils.get_channel_message_frequency(channel_id)
        action_value = random.randrange(1, 2 * response_frequency + 1)
        if action_value == 1:
            glaze = messageReactions.message_response("GLAZING")
            async with message.channel.typing():
                await asyncio.sleep(admin_utils.typing_speed(glaze))
                await message.channel.send(glaze)
            return
        elif action_value == 2:
            ragebait = messageReactions.message_response("RAGEBAITING")
            async with message.channel.typing():
                await asyncio.sleep(admin_utils.typing_speed(ragebait))
                await message.channel.send(ragebait)
            return

#THE FOLLOWING SECTION INITIALIZES AND EXECUTES BOT'S SLASH COMMANDS
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents) #command prefix is arbitrary, discord enforces slash commands


@client.tree.command(name="introduce", description="Give Kerkerkar permission to interact with current channel", guild=RBBT_SERVER_ID)
async def introduce_boneca(interaction: discord.Interaction):
    await interaction.response.defer() #discord invalidates slash command if it doesnt respond within 3 seconds :( this line buys us more time

    if interaction.user.guild_permissions.administrator:
        channel = (interaction.channel)
        channel_id = str(channel.id)
        if admin_utils.get_valid_channel(channel_id):
            await interaction.followup.send("I already have permissions to interact with {}!".format(interaction.channel.mention))
        else:
            await admin_utils.introduce(channel)
            await interaction.followup.send("You have given me permission to interact with {}!".format(interaction.channel.mention))

    else:
        await interaction.response.send_message("This command may only be used by admins of this server.")

@client.tree.command(name="banish", description="Remove Kerkerkar's permission to interact with current channel", guild=RBBT_SERVER_ID)
async def banish_boneca(interaction: discord.Interaction):
    if interaction.user.guild_permissions.administrator:
        channel = (interaction.channel)
        channel_id = str(channel.id)
        if admin_utils.get_valid_channel(channel_id):
            admin_utils.banish(channel_id)
            await interaction.response.send_message("Aw man :frowning2: you've taken away my permission to interact with {} :frowning2:".format(interaction.channel.mention))
        else:
            await interaction.response.send_message("I can't talk here anyway :joy_cat::pray:")
    else:
        await interaction.response.send_message("This command may only be used by admins of this server.")

@client.tree.command(name="frequency", description="Change Kerkerkar's message frequency", guild=RBBT_SERVER_ID)
async def frequency_boneca(interaction: discord.Integration, x: int):
    if interaction.user.guild_permissions.administrator:
        admin_utils.set_channel_message_frequency(str(interaction.channel.id), x)
        await interaction.response.send_message("I will now respond once every {} messages".format(x))
    else:
        await interaction.response.send_message("This command may only be used by admins of this server.")

@client.tree.command(name="help", description="Learn about Kerkerkar's functionality", guild=RBBT_SERVER_ID)
async def help_boneca(interaction: discord.Integration):
    boneca_overview = discord.Embed(title="BONECA AMBALABU PRE-RELEASE :frog:", 
                                  description="Hello, I'm Boneca - Discord's first ragebait bot! Welcome to my pre-release :partying_face: Currently, I specialize in dishing out ethical ragebait and top tier glazing. Keep your eyes peeled for further updates!", 
                                  color=discord.Color.green())
    
    getting_started = discord.Embed(title="TO GET STARTED :technologist:",
                                  description="Use /integrate to allow me to interact with the current channel. From there, carry on with your conversation and enjoy the ride :smiling_imp: I will aim to respond either once every 10 messages, or 8 times per day (choosing the lower rate).",
                                  color=discord.Color.green())
    
    settings = discord.Embed(title="SETTINGS COMMANDS :gear:",
                             description="Control Boneca's behaviour",
                             color=discord.Color.green())
    settings.add_field(name=":wave: /introduce", 
                       value="Give Boneca permission to interact with current channel", 
                       inline=False)
    settings.add_field(name=":door: /banish", 
                       value="Remove Boneca's permission to interact with current channel", 
                       inline=False)
    settings.add_field(name=":clock8: /frequency", 
                       value="Setting frequency to any value x will result in Boneca replying to one in x messages (OVERRIDES DEFAULT RESPONSE RATE)", 
                       inline=False)
    settings.add_field(name=":x: /notme", 
                       value="Toggle Boneca's permission to interact with you", 
                       inline=False)
    settings.add_field(name=":thumbsdown: /report", 
                       value="Flag Boneca's last message as innapropriate", 
                       inline=False)
    settings.add_field(name=":bulb: /suggest", 
                       value="Suggest features for future Boneca updates", 
                       inline=False)

    ragebait_glazing_commands = discord.Embed(title="RAGEBAIT + GLAZING COMMANDS :video_game:",
                                              description="Take advantage of Boneca's custom ragebait, glazing and mini-game commands",
                                              color=discord.Color.green())
    ragebait_glazing_commands.add_field(name="",
                                        value=":bangbang:**COMING SOON**:bangbang:")


    await interaction.response.send_message(embeds=[boneca_overview, getting_started, settings, ragebait_glazing_commands])

@client.tree.command(name="notme", description="Toggle Kerkerkar's permission to interact with you", guild=RBBT_SERVER_ID)
async def notme_boneca(interaction: discord.Integration):
    user = str(interaction.user.id)
    admin_utils.not_me(user)
    if admin_utils.get_dnt_user(user):
        await interaction.response.send_message("You've been added to Boneca's safe list. Boneca will never target you.")
    elif not admin_utils.get_dnt_user(user):
        await interaction.response.send_message("You've been removed from Boneca's safe list. Boneca will keep an eye out on you!")

@client.tree.command(name="report", description="Flag Kerkerkar's last message as innapropriate", guild=RBBT_SERVER_ID)
async def report_boneca(interaction: discord.Integration):
    channel = interaction.channel
    apologies = ["I'm sorry :worried: I took that too far... I've removed that prompt from my database.",
                 "I'm sorry :worried: I took that too far... I have asked the devs to review this one ASAP.",
                 "I can't figure out what I did wrong :disappointed: Please get in touch with @datkid10021 ASAP."]
    async for message in channel.history(limit=20):
        if message.author == client.user and message.content not in apologies:

            #FLICKS A DM TO THE REPORT CHANNEL OF RBBT
            report_channel = await client.fetch_channel(1402235942131208244)
            await report_channel.send("**{} ({}) used /report:** {}".format(interaction.user.name, interaction.user.id, message.content))

            #REMOVES MESSAGE
            report_status = admin_utils.report(message.content)
            await message.delete()
            if report_status:
                await interaction.response.send_message(apologies[0])
            else:
                await interaction.response.send_message(apologies[1])
            return
    await interaction.channel.send(apologies[2])

@client.tree.command(name="suggest", description="Suggest features for future Kerkerkar updates", guild=RBBT_SERVER_ID)
async def suggest_boneca(interaction: discord.Integration, suggestion: str):
    suggest_channel = await client.fetch_channel(1402236026084397138)
    await suggest_channel.send("**{} ({}) used /suggest:** {}".format(interaction.user.name, interaction.user.id, suggestion))
    await interaction.response.send_message("Thanks! I'll send you an update if the devs start working on this.")

async def memorial_checker():
    await client.wait_until_ready()
    while not client.is_closed():
        penthouse = await client.fetch_channel(PENTHOUSE_ID)
        testing_channel = await client.fetch_channel(1394643137657442376)
        now = datetime.datetime.now()
        if 17 <= now.hour < 24:
            try:
                event, message = memorial.memorial()
                if event == True:
                    await penthouse.send(message)
            except Exception as e:
                    await testing_channel.send(f"**EMERGENCY!** memorial_checker() IS BUSTED!: {e}")
        await asyncio.sleep(300)

#MANDATORY FOR BOT TO RUN
client.run(BOT_TOKEN)