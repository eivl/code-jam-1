# coding=utf-8
import asyncio
import json
import logging
import random
from typing import Any, Dict, List

from fuzzywuzzy import fuzz
from discord.ext.commands import AutoShardedBot, Context, command, BadArgument

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

        # Not final data
        with open('data.json', 'r') as f:
            self.data = json.load(f)

    async def disambiguate(self, ctx: Context, entries: List[str], timeout: int = 30):
        """
        Has the user choose between multiple entries in case one could not be chosen automatically.

        :param ctx: Context object from discord.py
        :param entries: List of items for user to choose from
        :param timeout: Number of seconds to wait before canceling disambiguation
        :return: Users choice for correct entry.
        """
        # allow names too and not only numbers?
        if len(entries) == 0:
            raise BadArgument('No matches found.')

        if len(entries) == 1:
            return entries[0]

        choices = '\n'.join('{0}: {1}'.format(index, entry) for index, entry in enumerate(entries, start=1))
        await ctx.send('Found multiple entries. Please choose the correct one.\n```' + choices + '```')

        def check(message):
            return (message.content.isdigit() and
                    message.author == ctx.author and
                    message.channel == ctx.channel)

        try:
            message = await self.bot.wait_for('message', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            raise BadArgument('Timed out.')

        # Guaranteed to not error because of isdigit() in check
        index = int(message.content)

        try:
            return entries[index - 1]
        except IndexError:
            raise BadArgument('Invalid choice.')

    def get_potential_matches(self, name):
        # TODO
        # - make this a converter instead
        # - nested disambiguation?
        # - convert to scientific name in converter for an easier time
        # - custom Context object hoo boy

        if name is None:
            # Need list cast because choice() uses indexing internally
            return [random.choice(list(self.data.values()))]

        def predicate(item):
            nonlocal name
            item, name = item.lower(), name.lower()
            return fuzz.partial_ratio(item, name) > 80 or fuzz.ratio(item, name) > 80

        # Maybe they should be separate
        return [item for item in self.data.keys() | self.data.values() if predicate(item)]

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

    @command()
    async def get(self, ctx: Context, name: str = None):
        """
        Go online and fetch information about a snake

        This should make use of your `get_snek` method, using it to get information about a snake. This information
        should be sent back to Discord in an embed.

        :param ctx: Context object passed from discord.py
        :param name: Optional, the name of the snake to get information for - omit for a random snake
        """
        items = self.get_potential_matches(name)
        result = await self.disambiguate(ctx, items)
        await ctx.send(result)

    async def on_command_error(self, ctx, error):
        # Temporary
        if not isinstance(error, BadArgument):
            return

        await ctx.send(str(error))

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
