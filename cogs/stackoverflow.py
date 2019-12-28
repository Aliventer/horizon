from discord.ext import commands
import typing

from cogs.utils.paginator import Pages


class StackOverflow(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_request(self, size, q):
        url = 'https://api.stackexchange.com/2.2/search/advanced?pagesize={}&order=desc&sort=relevance&q={}&site=stackoverflow'
        async with self.bot.session.get(url.format(size, q)) as r:
            return await r.json()

    @commands.command()
    async def search(self, ctx, size: typing.Optional[int] = 15, *, query):
        """Search for a given problem on StackOverflow"""
        response = await self.send_request(size, query)
        for item in response['items']:
            pass

        entries = [f'[{r["title"]}]({r["link"]})' for r in response['items']]
        p = Pages(ctx, entries=entries, per_page=10, show_entry_count=False)
        p.embed.set_thumbnail(url='https://cdn.sstatic.net/Sites/stackoverflow/company/img/logos/so/so-icon.png')
        p.embed.set_author(name=ctx.author.display_name + '#' + ctx.author.discriminator, icon_url=str(ctx.author.avatar_url))
        await p.paginate()


def setup(bot):
    bot.add_cog(StackOverflow(bot))
