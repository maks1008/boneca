import discord

class Client(discord.client): #necessary for the bot to run
    async def on_ready(self): #this function executes when the bot first goes online
        print("{} is back!".format(self.user))
    
intents = discord.Intents.default() #enables intents
intents.message_content = True


client = Client(intents=intents)
client.run("") #token goes here