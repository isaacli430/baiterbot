import discord, mtranslate
from discord.ext import commands
from contextlib import redirect_stdout
import inspect, aiohttp, asyncio, io, textwrap, traceback, os, json, urbanasync
from cogs import Cog
import random
from paginator import PaginatorSession

class BaiterBot(commands.Bot):

    def __init__(self):
        super().__init__(command_prefix="!")
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.urban_client = urbanasync.Client(session=self.session)

    def paginate(self, text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text)-1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))

    async def on_connect(self):
        self.remove_command('help')
        for name, func in inspect.getmembers(self):
            if isinstance(func, commands.Command):
                self.add_command(func)
        for cog in Cog.all_cogs(Cog):
            try:
                self.add_cog(cog(self))
                print(f"Added cog: {cog.__name__}")
            except Exception as e:
                print(f"ERROR: {e}")

    async def on_ready(self):
        perms = discord.Permissions.none()
        perms.administrator = True
        print(f"Bot is ready! Invite: {discord.utils.oauth_url(self.user.id, perms)}")
        await discord.utils.get(discord.utils.get(self.guilds, id=440819711924764672).text_channels, name="general").send("hello my fello baiters")

    
BaiterBot().run("NDY3MjkwMTgzOTYwNzU2MjI1.DiodcQ.lDjhbL_bXqzfoYdil9omtY34Lag")