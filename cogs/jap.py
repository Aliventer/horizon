from io import BytesIO
from functools import partial
from itertools import product
import time

from discord.ext import commands
import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps


class APIError(commands.CommandError):
    pass


class Jap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_img_url(self) -> str:
        base_url = 'https://neko-love.xyz/api/v1/neko'
        async with self.bot.session.get(base_url) as r:
            if r.status != 200:
                raise APIError(f'Failed to get an image link. Status code: {r.status}.')

            parsed = await r.json()
            return parsed['url']

    async def fetch_img(self) -> BytesIO:
        img_url = await self.get_img_url()
        async with self.bot.session.get(img_url) as r:
            if r.status != 200:
                raise APIError(f'Failed to fetch the image. Status code: {r.status}, URL: {img_url}.')

            raw_img_bytes = await r.read()
        return BytesIO(raw_img_bytes)

    @staticmethod
    def processing(img_buffer: BytesIO, string: str) -> BytesIO:
        size = 500
        border_width = 2
        border_color = '#1A2026'
        text_color = '#F2F4F6'

        with Image.open(img_buffer).convert('RGB') as im:
            with ImageOps.fit(im, (size, size), method=3) as normalized:
                draw = ImageDraw.Draw(normalized)
                font_size = int(0.9 * size / len(string))
                font = ImageFont.truetype('fonts/KosugiMaru.ttf', font_size)

                text_w, text_h = font.getsize(string)
                for dx, dy in product(range(-border_width, border_width + 1), repeat=2):
                    draw.text(((size - text_w) / 2 + dx, (size - text_h) / 2 + dy), string, font=font, fill=border_color)

                draw.text(((size - text_w) / 2, (size - text_h) / 2), string, font=font, fill=text_color)

                final_buffer = BytesIO()
                normalized.save(final_buffer, 'PNG')

        final_buffer.seek(0)
        return final_buffer

    @commands.command()
    async def test(self, ctx, *, string):
        start = time.time()
        async with ctx.typing():
            img_buffer = await self.fetch_img()
            fn = partial(self.processing, img_buffer, string)
            final_buffer = await self.bot.loop.run_in_executor(None, fn)

            # could be anything as long as filenames in
            # file and embed constructors are the same
            filename = 'neko.png'
            f = discord.File(filename=filename, fp=final_buffer)
            e = discord.Embed(colour=discord.Colour.blurple()) \
                .set_image(url=f'attachment://{filename}') \
                .set_footer(text=f'Took {(time.time() - start):.2} seconds.')
            await ctx.send(file=f, embed=e)

    @test.error
    async def test_error(self, ctx, error):
        if isinstance(error, APIError):
            await ctx.send('Cannot load background image atm. Try again later?')


def setup(bot):
    bot.add_cog(Jap(bot))
