import datetime
import sys
import traceback

import aiohttp
import discord
from discord.ext import commands


import config

description = 'A multi-purpose bot created by Aliventer#5827 ' \
    'with Python and <3.'

initial_extensions = (
    'cogs.meta',
    'cogs.stackoverflow',
    'cogs.jap',
    'cogs.reminder',
    'cogs.admin',
)


def _prefix_callable(bot, msg):
    user_id = bot.user.id
    base = ['hz ', f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('!')
        base.append('?')
    return base


class Horizon(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=_prefix_callable,
                         description=description, case_insensitive=True)
        self.session = aiohttp.ClientSession(loop=self.loop)

        for ext in initial_extensions:
            try:
                self.load_extension(ext)
            except Exception:
                print(f'Failed to load extension {ext}:', file=sys.stderr)
                traceback.print_exc()

        async def init_database():
            async with self.pool.acquire() as conn:
                for cog in self.cogs.values():
                    if hasattr(cog, 'init_table') and callable(cog.init_table):
                        await cog.init_table(conn)

        self.loop.create_task(init_database())

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(
                'This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send(
                'This command is disabled and cannot be used.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f'{ctx.author.name}#{ctx.author.discriminator} '
                           'is not in the sudoers file. '
                           'This incident will be reported.')
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}',
                      file=sys.stderr)
        elif isinstance(error, (commands.MissingRequiredArgument,
                                commands.TooManyArguments)):
            await ctx.send_help(ctx.command)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        print(
            f'Logged in as {self.user.name}#{self.user.discriminator} '
            f'(ID: {self.user.id})')

    async def on_resumed(self):
        print(f'\n[*] {self.user} resumed...')

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    def run(self):
        super().run(config.token, reconnect=True)

    async def close(self):
        await super().close()
        await self.session.close()
