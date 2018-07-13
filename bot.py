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

    @commands.command()
    async def urban(self, ctx, *, search_term):
        '''Searches for a term in Urban Dictionary'''
        try:
            definition_number = int(search_term.split(" ")[-1])-1
        except:
            definition_number = 0
        try:
            term = await self.urban_client.get_term(search_term)
        except LookupError:
            return await ctx.send("Term does not exist!")
        definition = term[definition_number]
        em = discord.Embed(title=definition.word, description=definition.definition, color=0x181818)
        em.add_field(name="Example", value=definition.example)
        em.add_field(name="Popularity", value=f"{definition.upvotes} 👍 {definition.downvotes} 👎")
        em.add_field(name="Author", value=definition.author)
        em.add_field(name="Permalink", value=f"[Click here!]({definition.permalink})")
        await ctx.send(embed=em)

    @commands.command(name='help')
    async def _help(self, ctx, command=None):
        '''Shows this page'''
        ems = []
        for cog in Cog.all_cogs(Cog):
            if cog.__name__ == "ReactWait":
                continue
            em = discord.Embed(title='Help', color=0x181818)
            em.set_author(name='Royale Prestige Series', icon_url=self.user.avatar_url)
            em.add_field(name=cog.__name__, value="```\n"+'\n\n'.join([f"{ctx.prefix}{attr.name}{' '*(15-len(attr.name))}{attr.short_doc}" for name, attr in inspect.getmembers(cog) if isinstance(attr, commands.Command)])+'\n```')
            ems.append(em)
        if command:
            command = discord.utils.get(self.commands, name=command.lower())
            return await ctx.send(embed=discord.Embed(color=0x181818, title=f"``{ctx.prefix}{command.signature}``", description=command.short_doc))
        comms = []
        for command in self.commands:
            if command.cog_name == "RPSBot" and not command.hidden:
                comms.append(f"{ctx.prefix}{command.name}{' '*(15-len(command.name))}{command.short_doc}")
        em = discord.Embed(title='Help', color=0x181818)
        em.set_author(name='Royale Prestige Series', icon_url=self.user.avatar_url)
        em.add_field(name="Bot Related", value=f"```\n"+'\n\n'.join(comms)+"\n```")
        ems.append(em)
        session = PaginatorSession(ctx=ctx, pages=ems, footer_text="Type !help command for more info on a command.")
        await session.run()

    
BaiterBot().run("NDY3MjkwMTgzOTYwNzU2MjI1.DiodcQ.lDjhbL_bXqzfoYdil9omtY34Lag")