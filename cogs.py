import discord
from discord.ext import commands
from contextlib import redirect_stdout
from reactwait import ReactWait
import youtube_dl
import inspect, aiohttp, asyncio, io, textwrap, traceback, os, ctypes, re, json, random, datetime

class Cog:
    def __init__(self, bot):
        self.bot = bot

    def all_cogs(clss):
        attrs = []
        for name, attr in inspect.getmembers(clss):
            if inspect.isclass(attr):
                if attr.__name__ != "type":
                    attrs.append(attr)
        return attrs

    class Moderator:
        def __init__(self, bot):
            self.bot = bot
            self.session = bot.session

        @commands.command(aliases=['clear'])
        @commands.has_permissions(manage_messages=True)
        async def purge(self, ctx, messages: int):
            '''Purge messages! This command isn't as crappy as the movie though.'''
            await ctx.message.delete()
            async for message in ctx.channel.history(limit=messages):
                await message.delete()
            await ctx.send(f"Deleted {messages} messages. 👍")

    class Fun:
        def __init__(self, bot):
            self.bot = bot
            self.session = bot.session

        @commands.command()
        async def urban(self, ctx, *, search_term):
            '''Searches for a term in Urban Dictionary'''
            try:
                definition_number = int(search_term.split(" ")[-1])-1
                search_term = search_term.rsplit(' ', 1)[0]
            except:
                definition_number = 0
            search_term = ''.join(search_term.split('"'))
            try:
                term = await self.urban_client.get_term(search_term)
            except LookupError:
                return await ctx.send("Term does not exist!")
            definition = term.definitions[definition_number]
            em = discord.Embed(title=definition.word, description=definition.definition, color=0x181818)
            em.add_field(name="Example", value=definition.example)
            em.add_field(name="Popularity", value=f"{definition.upvotes} 👍 {definition.downvotes} 👎")
            em.add_field(name="Author", value=definition.author)
            em.add_field(name="Permalink", value=f"[Click here!]({definition.permalink})")
            await ctx.send(embed=em)