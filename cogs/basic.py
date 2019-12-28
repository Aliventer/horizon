from discord.ext import commands
import discord

from cogs.utils.converters import to_separate_args

upvote = '<:upvote:660327748606099467>'
downvote = '<:downvote:660327764947107848>'


class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(self, ctx, *, content: to_separate_args):
        if len(content) > 11:
            # since there are only emojis for numbers up to ten
            return await ctx.send('Cannot create poll with more than 10 options.')

        full_name = ctx.author.display_name + '#' + ctx.author.discriminator
        question = content.pop(0)
        options = [f'`{i}.` {o}' for i, o in enumerate(content, start=1)]

        em = discord.Embed(title=question,
                           description='\n'.join(options),
                           colour=discord.Colour.blurple()) \
             .set_author(name=full_name,
                         icon_url=str(ctx.author.avatar_url))

        message = await ctx.send(embed=em)
        if len(options) == 0:
            for r in (upvote, downvote):
                await message.add_reaction(r)
        else:
            for i in range(1, len(options) + 1):
                reaction = '\N{keycap ten}' if i == 10 else f'{i}\N{combining enclosing keycap}'
                await message.add_reaction(reaction)


def setup(bot):
    bot.add_cog(Basic(bot))
