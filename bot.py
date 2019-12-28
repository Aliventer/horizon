import aiohttp
from discord.ext import commands
import datetime
import discord
import sys
import traceback

description = 'A multi-purpose bot created by Aliventer#5827 with Python and <3.'

initial_extensions = (
    'cogs.meta',
    'cogs.stackoverflow'
)


class Horizon(commands.Bot):
    def __init__(self, db):
        super().__init__(command_prefix='$', description=description, case_insensitive=True)
        self.session = aiohttp.ClientSession(loop=self.loop)

        for ext in initial_extensions:
            try:
                self.load_extension(ext)
            except Exception:
                print(f'Failed to load extension {ext}.', file=sys.stderr)
                traceback.print_exc()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send('This command cannot be used in private messages.')
        elif isinstance(error, commands.DisabledCommand):
            await ctx.author.send('This command is disabled and cannot be used.')
        elif isinstance(error, commands.CommandInvokeError):
            original = error.original
            if not isinstance(original, discord.HTTPException):
                print(f'In {ctx.command.qualified_name}:', file=sys.stderr)
                traceback.print_tb(original.__traceback__)
                print(f'{original.__class__.__name__}: {original}', file=sys.stderr)
        elif isinstance(error, commands.UserInputError):
            await ctx.send(error)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()

        print(f'Logged in as {self.user.name}#{self.user.discriminator} (ID: {self.user.id})')

    async def on_resumed(self):
        print(f'\n[*] {self.user} resumed...')

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    async def close(self):
        await super().close()
        await self.session.close()
