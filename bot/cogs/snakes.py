# coding=utf-8
import json
import logging
import re
import textwrap
from typing import Any, Dict

import aiohttp
import async_timeout
import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.converters import Snake

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    # I really hope this works
    wiki_sects = re.compile(r'(?:=+ (.*?) =+)(.*?\n\n)', flags=re.DOTALL)
    wiki_brief = re.compile(r'(.*?)(=+ (.*?) =+)', flags=re.DOTALL)

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def fetch(self, session, url):
        async with async_timeout.timeout(10):
            async with session.get(url) as response:
                return await response.json()

    async def get_snek(self, name: str = None) -> Dict[str, Any]:
        """
        Go online and fetch information about a snake

        The information includes the name of the snake, a picture of the snake, and various other pieces of info.
        What information you get for the snake is up to you. Be creative!

        If "python" is given as the snake name, you should return information about the programming language, but with
        all the information you'd provide for a real snake. Try to have some fun with this!

        :param name: Optional, the name of the snake to get information for - omit for a random snake
        :return: A dict containing information on a snake
        """
        snake_info = {}
        # python (programming language) pageid = 23862
        URL = "https://en.wikipedia.org/w/api.php?"
        ACTION = "action=query"
        LIST = "list=search"
        SRSEARCH = "srsearch="
        UTF8 = "utf8="
        SRLIMIT = "srlimit=1"
        FORMAT = "format=json"
        PROP = "prop=extracts|images|info"
        EXLIMIT = "exlimit=max"
        EXPLAINTEXT = "explaintext"
        INPROP = "inprop=url"

        PAGE_ID_URL = f"{URL}{FORMAT}&{ACTION}&{LIST}&{SRSEARCH}{name}&{UTF8}&{SRLIMIT}"

        async with aiohttp.ClientSession() as session:
            j = await self.fetch(session, PAGE_ID_URL)
            # wikipedia does have a error page
            try:
                PAGEID = j["query"]["search"][0]["pageid"]
            except Keyerror:
                PAGEID = 41118
            PAGEIDS = f"pageids={PAGEID}"

        snake_page = f"{URL}{FORMAT}&{ACTION}&{PROP}&{EXLIMIT}&{EXPLAINTEXT}&{INPROP}&{PAGEIDS}"

        async with aiohttp.ClientSession() as session:
            j = await self.fetch(session, snake_page)
            # constructing dict - handle exceptions later
            try:
                snake_info["title"] = j["query"]["pages"][f"{PAGEID}"]["title"]
                snake_info["extract"] = j["query"]["pages"][f"{PAGEID}"]["extract"]
                snake_info["images"] = j["query"]["pages"][f"{PAGEID}"]["images"]
                snake_info["fullurl"] = j["query"]["pages"][f"{PAGEID}"]["fullurl"]
                snake_info["pageid"] = j["query"]["pages"][f"{PAGEID}"]["pageid"]
            except:
                snake_info["error"] = True
            if snake_info["images"]:
                i_url = 'https://commons.wikimedia.org/wiki/Special:FilePath/'
                image_list = []
                map_list = []
                for image in snake_info["images"]:
                    i = image["title"].split(':')[1]
                    if 'Map' not in i:
                        image_list.append(f"{i_url}{i}")
                    else:
                        map_list.append(f"{i_url}{i}")
            snake_info["image_list"] = image_list
            snake_info["map_list"] = map_list
            log.info(image_list)
            log.info(map_list)
        return snake_info

    @command()
    async def get(self, ctx: Context, *, name: Snake = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        if name is None:
            name = Snake.random()

        data = await self.get_snek(name)

        match = self.wiki_brief.match(data['extract'])
        embed = discord.Embed(
            title=data['title'],
            description=match.group(1) if match else None,
            url=data['fullurl'],
            colour=0x59982F
        )

        fields = self.wiki_sects.findall(data['extract'])
        excluded = ('see also',)

        for title, body in fields:
            if title.lower() in excluded:
                continue
            if not body.strip():
                continue
            value = textwrap.shorten(body.strip(), width=200)
            embed.add_field(name=title, value=value + '\n\u200b', inline=False)

        embed.set_footer(text='Powered by Wikipedia')

        # TODO thumbnail in embed
        await ctx.send(embed=embed)

    async def on_command_error(self, ctx, error):
        # Temporary
        await ctx.send(str(error))

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
