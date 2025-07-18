import discord
import random
from botActions.ragebait.ragebait import ragebait
from botActions.glaze.glaze import glazing

#if random value == one of these, the respective response is triggered
glaze_value = 1
ragebait_value = 2

class Client(discord.Client): #necessary for the bot to run
    async def on_ready(self): #this function executes when the bot first goes online
        print("{} is back!".format(self.user))
    
    async def on_message(self, message): #when a message is sent
        action_value = random.randrange(1,121) # generates a number from 1 to 121
        if message.author == self.user:
            return
        if action_value == glaze_value:
            await message.channel.send(glazing())
        elif action_value == ragebait_value:
            await message.channel.send(ragebait())
        
    
intents = discord.Intents.default() #enables intents
intents.message_content = True


client = Client(intents=intents)
client.run("") #token goes here