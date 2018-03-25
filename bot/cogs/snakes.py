# coding=utf-8
import logging
import re
from typing import Any, Dict

import discord
from discord.ext.commands import AutoShardedBot, BadArgument, Context, command

from bot.converters import Snake

log = logging.getLogger(__name__)


class Snakes:
    """
    Snake-related commands
    """

    # I really hope this works
    wiki_re = re.compile(r'== (.*?) ==(.*?\n\n)', flags=re.DOTALL)

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

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
        # mock
        return {
            'pageid': 123456,
            'fullurl': 'https://en.wikipedia.org/wiki/Mozambique_spitting_cobra',
            'title': 'Mozambique spitting cobra',
            'extract': 'The Mozambique spitting cobra (Naja mossambica) is a species of spitting cobra native to Africa.\n\n\n== Description ==\nIn color the snake is slate to blue, olive or tawny black above, with some or all scales black-edging. Below, salmon pink to purple yellowish, with black bars across the neck and ventrals speckled or edged with brown or black; young specimens sometimes have pink or yellow bars on the throat.\nThe average length of adults is between 90 cm - 105 cm (3-3\u00bd feet), but largest specimen actually measured was a male 154 cm (5 feet) long. (Durban, Kwa-Zulu Natal, South Africa]).\n\n\n== Distribution ==\nThis species is the most common cobra of the savanna regions of the tropical and subtropical Africa. The distribution includes Natal, as far south as Durban, Mpumalanga Province Lowveld region, south-eastern Tanzania and Pemba Island and west to southern Angola and northern Namibia. Younger specimens are much more frequently encountered in the open at daytime. Unlike the Egyptian Cobra, this species prefers localities near water, to which it will readily take when disturbed.\n\n\n== Toxicology ==\nIt is considered one of the most dangerous snakes in Africa. Its venom is about as toxic as the American Mojave rattlesnake, considered the world\'s most venomous rattlesnake. Like the rinkhals, it can spit its venom. Its bite causes severe local tissue destruction (similar to that of the puff adder). Venom to the eyes can also cause impaired vision or blindness. The venom of this species contains postsynaptic neurotoxin and cytotoxin. There have been only a few fatalities resulting from bites of this species but survivors are mostly disfigured.\nA polyvalent antivenom is currently being developed by the Universidad de Costa Rica\'s Instituto Clodomiro Picado.\n\n\n== Diet ==\nThis cobra\'s diet mainly consists of amphibians, other snakes, birds, eggs, small mammals, and occasionally even insects.\n\n\n== Habits ==\nThis snake is nervous and temperamental. When confronted at close quarters, it can rear up as much as two-thirds of its length and spread its long narrow hood, and will readily "spit" in defense, usually from a reared-up position. The venom can be propelled 2\u20133 metres (6\u00bd-10 feet), with great accuracy. The spitting cobra might bite instead of spitting, depending on its circumstances, and like the rinkhals it may feign death to avoid further molestation.\n\n\n== Reproduction ==\nThe eggs average 10 to 22 in number, hatchlings measure 230-250mm.\n\n\n== References ==',
            'images': [
                {
                    'ns': 6,
                    'title': 'File:Map-Africa snakes Naja-mossambica.svg'
                }
            ]
        }

    @command()
    async def get(self, ctx: Context, name: Snake = None):
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
        embed = discord.Embed(title=data['title'], url=data['fullurl'], colour=0x59982F)

        fields = self.wiki_re.findall(data['extract'])

        # TODO embeds can probably get way too big, only show one to three sentences from each section?
        for title, body in fields:
            embed.add_field(name=title, value=body.strip() + '\n\u200b', inline=False)

        embed.set_footer(text='Powered by Wikipedia')

        # TODO thumbnail in embed
        await ctx.send(name, embed=embed)

    async def on_command_error(self, ctx, error):
        # Temporary
        if not isinstance(error, BadArgument):
            return

        await ctx.send(str(error))

    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
