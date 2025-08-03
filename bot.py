import random
import botActions.messageReactions as messageReactions
import commands.administrativeCommands.admin_utils as admin_utils
import discord
from discord import app_commands
from discord.ext import commands

MESSAGE_RESPONSE_FREQUENCY = 1 #HOW OFTEN BONECA RESPONDS
RBBT_SERVER_ID = discord.Object(id=1368129546578300978) #TESTING SERVER ID

class Client(commands.Bot):
    async def on_ready(self):
        """AS SOON AS BOT GOES ONLINE"""
        admin_utils.unpack()

        try:
            synced = await self.tree.sync(guild=RBBT_SERVER_ID) #FORCES BOT TO SYNC SLASH COMMANDS
            print("{} commands succesfully synced to {}".format(len(synced), RBBT_SERVER_ID.id))
        except Exception as e:
            print("ERROR: {}".format(e))

        print("{} is up and running!".format(self.user))
    
    async def on_message(self, message):
        """MESSAGE REACTIONS"""

        #IGNORES THE FOLLOWING MESSAGES
        if message.author == self.user:
            return
        if admin_utils.dnt_user(str(message.author.id)):
            return
        if not admin_utils.valid_channel(str(message.channel.mention)):
            return
        
        #RUNS TRIGGER WORD DETECTOR
        trigger = messageReactions.triggers_detected(message.content)
        if trigger is not False:
            await message.channel.send(messageReactions.trigger_message(trigger))
            return
        
        #GENERATES A MESSAGE RESPONSE (glazing/ragebait)
        if len(message.content.split()) > 2:
            action_value = random.randrange(1, 2 * MESSAGE_RESPONSE_FREQUENCY + 1)
            if action_value == 1:
                await message.channel.send(messageReactions.message_response("GLAZING"))
                return
            elif action_value == 2:
                await message.channel.send(messageReactions.message_response("RAGEBAITING"))
                return

#THE FOLLOWING SECTION INITIALIZES AND EXECUTES BOT'S SLASH COMMANDS
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents) #command prefix is arbitrary, discord enforces slash commands


@client.tree.command(name="introduce", description="Introduce Boneca to this channel", guild=RBBT_SERVER_ID)
async def introduce_boneca(interaction: discord.Interaction):
    channel_id = str(interaction.channel.mention)
    if admin_utils.valid_channel(channel_id):
        await interaction.response.send_message("I already have permissions to interact with {}!".format(interaction.channel.mention))
    else:
        admin_utils.introduce(channel_id)
        await interaction.response.send_message("You have given me permission to interact with {}!".format(interaction.channel.mention))

@client.tree.command(name="banish", description="Remove Boneca from this channel", guild=RBBT_SERVER_ID)
async def banish_boneca(interaction: discord.Interaction):
    channel_id = str(interaction.channel.mention)
    if admin_utils.valid_channel(channel_id):
        admin_utils.banish(channel_id)
        await interaction.response.send_message("Aw man :frowning2: you've taken away my permission to interact with {} :frowning2:".format(interaction.channel.mention))
    else:
        await interaction.response.send_message("I can't talk here anyway :joy_cat::pray:")

@client.tree.command(name="report", description="Flag Boneca's last message as innapropriate", guild=RBBT_SERVER_ID)
async def report_boneca(interaction: discord.Integration):
    channel = interaction.channel
    apologies = ["I'm sorry :worried: I took that too far... I've removed that prompt from my database.",
                 "I'm sorry :worried: I took that too far... I have asked the devs to review this one ASAP.",
                 "I can't figure out what I did wrong :disappointed: Please get in touch with @datkid10021 ASAP."]
    async for message in channel.history(limit=20):
        if message.author == client.user and message.content not in apologies:
            #FLICKS A DM TO datkid
            datkid = await client.fetch_user(572732144195993609)
            await datkid.send("**{} USED /REPORT:** {}".format(interaction.user.name, message.content))

            #REMOVES MESSAGE
            report_status = admin_utils.report(message.content)
            await message.delete()
            if report_status:
                await interaction.response.send_message(apologies[0])
            else:
                await interaction.response.send_message(apologies[1])
            return
    await interaction.channel.send(apologies[2])

@client.tree.command(name="notme", description="Toggle Boneca's permissions to interact with you", guild=RBBT_SERVER_ID)
async def notme_boneca(interaction: discord.Integration):
    user = str(interaction.user.id)
    admin_utils.not_me(user)
    if admin_utils.dnt_user(user):
        await interaction.response.send_message("You've been added to Boneca's safe list. Boneca will never target you.")
    elif not admin_utils.dnt_user(user):
        await interaction.response.send_message("You've been removed from Boneca's safe list. Boneca will keep an eye out on you!")


#MANDATORY FOR BOT TO RUN
client.run("") #token goes here