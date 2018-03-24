import json
import random

from discord.ext.commands import Converter
from fuzzywuzzy import fuzz

from bot.utils import disambiguate


class Snake(Converter):
    with open('snakes.json', 'r') as f:
        snakes = json.load(f)

    async def convert(self, ctx, name):
        def get_potential(iterable, *, threshold=80):
            nonlocal name

            name = name.lower()
            for item in iterable:
                a, b = fuzz.ratio(name, item.lower()), fuzz.partial_ratio(name, item.lower())

                if a >= threshold or b >= threshold:
                    yield item

        scientific = list(get_potential(self.snakes.values()))
        if scientific:
            return await disambiguate(ctx, scientific)

        common = list(get_potential(self.snakes.keys()))
        return await disambiguate(ctx, common)

    @classmethod
    def random(cls):
        # list cast necessary because choice() uses indexing internally
        return random.choice(list(cls.snakes.values()))
