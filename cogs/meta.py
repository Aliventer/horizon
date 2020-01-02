import itertools

from discord.ext import commands
import discord

from .utils.paginator import HelpPaginator
from .utils.converters import to_separate_args


class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={
            'cooldown': commands.Cooldown(1, 3.0, commands.BucketType.member),
            'help': 'Shows help about the bot, a command, or a category.'
        })

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(str(error.original))

    def get_command_signature(self, command):
        parent = command.full_parent_name
        if len(command.aliases) > 0:
            aliases = '|'.join(command.aliases)
            fmt = f'[{command.name}|{aliases}]'
            if parent:
                fmt = f'{parent} {fmt}'
            alias = fmt
        else:
            alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {command.signature}'

    async def send_bot_help(self, mapping):
        def key(c):
            # use zero-width space to put "No Category" at the
            # beginning after sorting.
            return c.cog_name or '\u200bNo Category'

        bot = self.context.bot
        entries = await self.filter_commands(bot.commands, sort=True, key=key)
        nested_pages = []
        per_page = 9
        total = 0

        for cog, cmds in itertools.groupby(entries, key=key):
            cmds = sorted(cmds, key=lambda c: c.name)
            if len(cmds) == 0:
                continue

            total += len(cmds)
            actual_cog = bot.get_cog(cog)
            # get the description if it exists (and the cog is valid) or return Empty embed.
            description = (actual_cog and actual_cog.description) or discord.Embed.Empty
            nested_pages.extend((cog, description, cmds[i:i + per_page]) for i in range(0, len(cmds), per_page))

        pages = HelpPaginator(self, self.context, nested_pages, per_page=1)

        pages.get_page = pages.get_bot_page
        pages.is_bot = True
        pages.total = total
        await pages.paginate()

    async def send_cog_help(self, cog):
        entries = await self.filter_commands(cog.get_commands(), sort=True)
        pages = HelpPaginator(self, self.context, entries)
        pages.title = f'{cog.qualified_name} Commands'
        pages.description = cog.description

        await pages.paginate()

    def common_command_formatting(self, page_or_embed, command):
        page_or_embed.title = self.get_command_signature(command)
        if command.description:
            page_or_embed.description = f'{command.description}\n\n{command.help}'
        else:
            page_or_embed.description = command.help or 'No help found...'

    async def send_command_help(self, command):
        embed = discord.Embed(colour=discord.Colour.blurple())
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group):
        subcommands = group.commands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        pages = HelpPaginator(self, self.context, entries)
        self.common_command_formatting(pages, group)

        await pages.paginate()


class Meta(commands.Cog):
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.old_help_command

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, *, question_and_options: to_separate_args):
        """Makes a poll quickly.
        The first argument is the question and the rest are the options.
        Arguments are separated by "|".
        """
        if len(question_and_options) > 11:
            # since there are only emojis for numbers up to ten
            return await ctx.send('Cannot create poll with more than 10 options.')

        full_name = ctx.author.display_name + '#' + ctx.author.discriminator
        question = question_and_options[0]
        options = [f'`{i}.` {o}' for i, o in enumerate(question_and_options[1:], start=1)]

        em = discord.Embed(title=question,
                           description='\n'.join(options),
                           colour=discord.Colour.blurple()) \
             .set_author(name=full_name,
                         icon_url=str(ctx.author.avatar_url))

        message = await ctx.send(embed=em)

        try:
            await ctx.message.delete()
        except:
            pass

        if len(options) == 0:
            for r in ('<:upvote:660327748606099467>', '<:downvote:660327764947107848>'):
                await message.add_reaction(r)
        else:
            for i in range(1, len(options) + 1):
                reaction = '\N{keycap ten}' if i == 10 else f'{i}\N{combining enclosing keycap}'
                await message.add_reaction(reaction)


def setup(bot):
    bot.add_cog(Meta(bot))
