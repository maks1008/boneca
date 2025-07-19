import discord
import random
import botActions.messageReactions as messageReactions

MESSAGE_RESPONSE_FREQUENCY = 3

class Client(discord.Client):
    async def on_ready(self):
        print("{} is back!".format(self.user))
    
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
        if action_value == 1:
            await message.channel.send(messageReactions.message_response("GLAZING"))
            return
        elif action_value == 2:
            await message.channel.send(messageReactions.message_response("RAGEBAITING"))
            return
        
    
intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run("") #token goes here