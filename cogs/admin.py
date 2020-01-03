import textwrap
import traceback
from contextlib import redirect_stdout
from io import StringIO

from discord.ext import commands

from .utils.converters import prepare_bot_module


class Admin(commands.Cog):
    """Admin-only commands."""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    async def cog_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @staticmethod
    def cleanup_code(content):
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        return content

    @staticmethod
    async def message_or_reaction(ctx, reaction_string):
        try:
            await ctx.message.add_reaction(reaction_string)
        except:
            await ctx.send(reaction_string)

    @commands.command(hidden=True)
    async def load(self, ctx, *, module: prepare_bot_module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await self.message_or_reaction(ctx, '\u2705')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module: prepare_bot_module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await self.message_or_reaction(ctx, '\u2705')

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module: prepare_bot_module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await self.message_or_reaction(ctx, '\u2705')

    @commands.command(name='eval', pass_context=True, hidden=True)
    async def eval_(self, ctx, *, body: str):
        """Evaluates a code."""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Admin(bot))
