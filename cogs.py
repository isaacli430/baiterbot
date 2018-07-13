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