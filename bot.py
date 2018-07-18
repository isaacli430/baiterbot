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
        self._last_result = None
        self.session = aiohttp.ClientSession(loop=self.loop)

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

    async def on_member_join(self, member):
        await discord.utils.get(member.guild.text_channels, name="welcome").send(f"Hey {member.mention}, welcome to Masters Of Baiting! Please read the #rules. Suggestions are always welcome too. To suggest do `!suggest <suggestion>`. Enjoy your stay here!\n\nInvite link: https://discord.gg/MtpjRff")

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CheckFailure):
            return await ctx.send("You don't have the permissions to run that command!")
        await ctx.send(embed=discord.Embed(color=0x181818, title=f"``{ctx.prefix}{ctx.command.signature}``", description=ctx.command.short_doc))
        raise error

    @commands.command()
    async def suggest(self, ctx, *, message):
        '''Suggest a feature to the Lord and Almighty Masterbaiter'''
        em = discord.Embed(color=discord.Color.green(), title="Suggestion", description=message)
        em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await discord.utils.get(ctx.guild.text_channels, id=441176963093364736).send(embed=em)

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
            if command.cog_name == "BaiterBot" and not command.hidden:
                comms.append(f"{ctx.prefix}{command.name}{' '*(15-len(command.name))}{command.short_doc}")
        em = discord.Embed(title='Help', color=0x181818)
        em.set_author(name='Royale Prestige Series', icon_url=self.user.avatar_url)
        em.add_field(name="Bot Related", value=f"```\n"+'\n\n'.join(comms)+"\n```")
        ems.append(em)
        session = PaginatorSession(ctx=ctx, pages=ems, footer_text="Type !help command for more info on a command.")
        await session.run()

    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str, edit=False):
        """Evaluates python code"""

        if ctx.author.id != 295368465005543424:
            return

        env = {
            'bot': self,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result,
            'source': inspect.getsource
        }

        env.update(globals())

        body = self.cleanup_code(body)
        if edit: await self.edit_to_codeblock(ctx, body)
        stdout = io.StringIO()
        err = out = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            err = await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
            return await err.add_reaction('\u2049')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            if "MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs" in value:
                value = value.replace("MzgxNzM2MjYyOTgzMzUyMzIw.DPLfIA.3K0eC2WGtCtrmF7wFJPYJxZLCDs", "[EXPUNGED]")
            if ret is None:
                if value:
                    try:
                        out = await ctx.send(f'```py\n{value}\n```')
                    except:
                        paginated_text = self.paginate(value)
                        for page in paginated_text:
                            if page == paginated_text[-1]:
                                out = await ctx.send(f'```py\n{page}\n```')
                                break
                            await ctx.send(f'```py\n{page}\n```')
            else:
                self._last_result = ret
                try:
                    out = await ctx.send(f'```py\n{value}{ret}\n```')
                except:
                    paginated_text = self.paginate(f"{value}{ret}")
                    for page in paginated_text:
                        if page == paginated_text[-1]:
                            out = await self.send(f'```py\n{page}\n```')
                            break
                        await ctx.send(f'```py\n{page}\n```')

        if out:
            await out.add_reaction('\u2705')  # tick
        elif err:
            await err.add_reaction('\u2049')  # x
        else:
            await ctx.message.add_reaction('\u2705')

    async def edit_to_codeblock(self, ctx, body, pycc='blank'):
        if pycc == 'blank':
            msg = f'{ctx.prefix}eval\n```py\n{body}\n```'
        else:
            msg = f'{ctx.prefix}cc make {pycc}\n```py\n{body}\n```'
        await ctx.message.edit(content=msg)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    def get_syntax_error(self, e):
        if e.text is None:
            return f'```py\n{e.__class__.__name__}: {e}\n```'
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    
BaiterBot().run("NDY3MjkwMTgzOTYwNzU2MjI1.DiodcQ.lDjhbL_bXqzfoYdil9omtY34Lag")