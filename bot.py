import random
import botActions.messageReactions as messageReactions
import commands.administrativeCommands.admin_utils as admin_utils
import discord
from discord import app_commands
from discord.ext import commands

MESSAGE_RESPONSE_FREQUENCY = 4
RBBT_SERVER_ID = discord.Object(id=1368129546578300978)

class Client(commands.Bot):
    async def on_ready(self):
        print("{} is back!".format(self.user))

        try:
            synced = await self.tree.sync(guild=RBBT_SERVER_ID)
            print("{} commands succesfully synced to {}".format(len(synced), RBBT_SERVER_ID.id))

        except Exception as e:
            print("ERROR: {}".format(e))

    
    async def on_message(self, message):
        #IGNORES ITS OWN MESSAGES
        if message.author == self.user:
            return
        
        #RUNS TRIGGER WORD DETECTOR
        trigger = messageReactions.triggers_detected(message.content)
        if trigger is not False:
            await message.channel.send(messageReactions.trigger_message(trigger))
            return

        #GENERATES A MESSAGE RESPONSE (glazing/ragebait)
        action_value = random.randrange(1, 2 * MESSAGE_RESPONSE_FREQUENCY + 1)
        if action_value == 1 and admin_utils.accepted_channel(str(message.channel.mention)):
            await message.channel.send(messageReactions.message_response("GLAZING"))
            return
        elif action_value == 2 and admin_utils.accepted_channel(str(message.channel.mention)):
            await message.channel.send(messageReactions.message_response("RAGEBAITING"))
            return
        
intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents) #command prefix is arbitrary, discord enforces slash commands

@client.tree.command(name="introduce", description="introduces boneca into this channel", guild=RBBT_SERVER_ID)
async def introduce_boneca(interaction: discord.Interaction):
    channel_id = str(interaction.channel.mention)
    if admin_utils.accepted_channel(channel_id):
        await interaction.response.send_message("I already have permissions to talk here! What are you doing? Give me more permissions than everyone else?!")
    else:
        admin_utils.introduce(channel_id)
        await interaction.response.send_message("You have given me permission to interact with {}!".format(interaction.channel.mention))

@client.tree.command(name="banish", description="removes boneca from this channel", guild=RBBT_SERVER_ID)
async def banish_boneca(interaction: discord.Interaction):
    channel_id = str(interaction.channel.mention)
    if admin_utils.accepted_channel(channel_id):
        admin_utils.banish(channel_id)
        await interaction.response.send_message("Aw man :frowning2: you've taken away my permission to interact with {} :frowning2:".format(interaction.channel.mention))
    else:
        await interaction.response.send_message("I can't talk here anyway :joy_cat::pray:")

@client.tree.command(name="report", description="flag boneca's last message as innapropriate", guild=RBBT_SERVER_ID)
async def report_boneca(interaction: discord.Integration):
    channel = interaction.channel
    async for message in channel.history(limit=20):
        if message.author == client.user:
            
            datkid = await client.fetch_user(572732144195993609)
            await datkid.send("**{} USED /REPORT:** {}".format(interaction.user.name, message.content))

            report_status = admin_utils.report(message.content)
            await message.delete()
            if report_status:
                await interaction.response.send_message("I'm sorry :worried: I took that too far... I've removed that prompt from my database.")
            else:
                await interaction.response.send_message("I'm sorry :worried: I took that too far... I have asked the devs to review this one ASAP.")
            return
        
    await interaction.channel.send("I can't figure out what I did wrong :disappointed: Please get in touch with @datkid10021 ASAP.")



client.run("") #token goes here