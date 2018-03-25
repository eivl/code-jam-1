import json
import random

from discord.ext.commands import Converter

from fuzzywuzzy import fuzz

from bot.utils import disambiguate


class Snake(Converter):
    with open('snakes.json', 'r') as f:
        snakes = json.load(f)

    async def convert(self, ctx, name):
        if name.lower() == 'python':
            return 'Python (programming language)'

        def get_potential(iterable, *, threshold=80):
            nonlocal name

            name = name.lower()
            for item in iterable:
                a, b = fuzz.ratio(name, item.lower()), fuzz.partial_ratio(name, item.lower())

                if a >= threshold or b >= threshold:
                    yield item

        all_names = self.snakes.keys() | self.snakes.values()
        timeout = len(all_names) * (3 / 4)

        name = await disambiguate(ctx, list(get_potential(all_names)), timeout=timeout, colour=0x59982F)
        return self.snakes.get(name, name)

    @classmethod
    def random(cls):
        # list cast necessary because choice() uses indexing internally
        return random.choice(list(cls.snakes.values()))
