# coding=utf-8
import asyncio
from typing import List

import discord
from discord.ext.commands import BadArgument, Context

from bot.pagination import LinePaginator


async def disambiguate(ctx: Context, entries: List[str], timeout: float = 30):
    """
    Has the user choose between multiple entries in case one could not be chosen automatically.

    :param ctx: Context object from discord.py
    :param entries: List of items for user to choose from
    :param timeout: Number of seconds to wait before canceling disambiguation
    :return: Users choice for correct entry.
    """
    if len(entries) == 0:
        raise BadArgument('No matches found.')

    if len(entries) == 1:
        return entries[0]

    choices = (f'{index}: {entry}' for index, entry in enumerate(entries, start=1))

    def check(message):
        return (message.content.isdigit() and
                message.author == ctx.author and
                message.channel == ctx.channel)

    try:
        embed = discord.Embed(title='Found multiple choices. Please choose the correct one.', colour=0x59982F)
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        coro1 = ctx.bot.wait_for('message', check=check, timeout=timeout)
        coro2 = LinePaginator.paginate(choices, ctx, embed=embed, max_lines=20,
                                       empty=False, max_size=1500, timeout=9000)

        # wait_for timeout will go to except instead of the wait_for thing as I expected
        futures = [asyncio.ensure_future(coro1), asyncio.ensure_future(coro2)]
        done, pending = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED, loop=ctx.bot.loop)

        for coro in pending:
            coro.cancel()

        # :yert:
        result = list(done)[0].result()

        if result is None:
            raise BadArgument('Canceled.')
    except asyncio.TimeoutError:
        raise BadArgument('Timed out.')

    # Guaranteed to not error because of isdigit() in check
    index = int(result.content)

    try:
        return entries[index - 1]
    except IndexError:
        raise BadArgument('Invalid choice.')


class CaseInsensitiveDict(dict):
    """
    We found this class on StackOverflow. Thanks to m000 for writing it!

    https://stackoverflow.com/a/32888599/4022104
    """

    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super(CaseInsensitiveDict, self).__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(self.__class__._k(key))

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key):
        return super(CaseInsensitiveDict, self).__delitem__(self.__class__._k(key))

    def __contains__(self, key):
        return super(CaseInsensitiveDict, self).__contains__(self.__class__._k(key))

    def pop(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).pop(self.__class__._k(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).get(self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super(CaseInsensitiveDict, self).setdefault(self.__class__._k(key), *args, **kwargs)

    def update(self, E=None, **F):
        super(CaseInsensitiveDict, self).update(self.__class__(E))
        super(CaseInsensitiveDict, self).update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)
