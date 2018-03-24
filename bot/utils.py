# coding=utf-8
import asyncio
from typing import List

from discord.ext.commands import BadArgument, Context


async def disambiguate(ctx: Context, entries: List[str], timeout: int = 30):
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

    choices = '\n'.join(f'{index}: {entry}' for index, entry in enumerate(entries, start=1))
    await ctx.send('Found multiple entries. Please choose the correct one.\n```' + choices + '```')

    def check(message):
        return (message.content.isdigit() and
                message.author == ctx.author and
                message.channel == ctx.channel)

    try:
        message = await ctx.bot.wait_for('message', check=check, timeout=timeout)
    except asyncio.TimeoutError:
        raise BadArgument('Timed out.')

    # Guaranteed to not error because of isdigit() in check
    index = int(message.content)

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
