import discord
from discord.ext import commands

import pathlib
from cogs.utils.dataIO import dataIO
import aiohttp

import io
from .utils import checks

path = 'data/exilium/exmboard'

#bot = commands.Bot(command_prefix=commands.when_mentioned, description="Battlefield Stats Tracker")

class ExmBoard:

    __author__ = "mengy007 (mengy#1441)"
    __version__ = "1.0"

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        try:
            self.settings = dataIO.load_json(path + '/settings.json')
        except Exception:
            self.settings = {}

    def save_json(self):
        dataIO.save_json(path + '/settings.json', self.settings)

    def init_server(self, server: discord.Server, reset=False):
        if server.id not in self.settings or reset:
            self.settings[server.id] = {
              'whitelist': [],
              'players': []
            }

    @commands.group(name='exmboardset', pass_context=True, no_pm=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def _group(self, ctx):
        """
        settings for leaderboard
        """

        if ctx.invoked_subcommand is None:
            #await self.bot.send_help(ctx)
            #await ctx.send_help()
            await self.send_cmd_help(ctx)

    @_group.command(name='add', pass_context=True, no_pm=True)
    async def add(self, ctx, playername):
        """
        add a player to be tracked on leaderboard
        """

        server = ctx.message.server
        self.init_server(server)

        if playername in self.settings[server.id]['players']:
            return await self.bot.say('Player already on leaderboard')
        self.settings[server.id]['players'].append(playername)
        self.save_json()
        await self.bot.say('Player added to leaderboard')

    @_group.command(name='remove', pass_context=True, no_pm=True)
    async def remove(self, ctx, playername):
        """
        remove a player from being tracked on leaderboard
        """

        server = ctx.message.server
        self.init_server(server)

        if playername in self.settings[server.id]['players']:
            self.settings[server.id]['players'].remove(playername)
            self.save_json()
            return await self.bot.say('Player removed from leaderboard')
        await self.bot.say('Player not on leaderboard')

    @_group.command(name='whitelist', pass_context=True, no_pm=True)
    async def whitelist(self, ctx, channel: discord.Channel):
        """
        add a channel where the leaderboard is allowed (if you want)
        """

        server = ctx.message.server
        self.init_server(server)

        if channel.id in self.settings[server.id]['whitelist']:
            return await self.bot.say('Channel already whitelisted')
        self.settings[server.id]['whitelist'].append(channel.id)
        self.save_json()
        await self.bot.say('Channel whitelisted.')

    @_group.command(name='unwhitelist', pass_context=True, no_pm=True)
    async def unwhitelist(self, ctx, channel: discord.Channel):
        """
        unwhitelist a channel
        """

        server = ctx.message.server
        self.init_server(server)

        if channel.id not in self.settings[server.id]['whitelist']:
            return await self.bot.say('Channel wasn\'t whitelisted')
        self.settings[server.id]['whitelist'].remove(channel.id)
        self.save_json()
        await self.bot.say('Channel unwhitelisted.')

    @_group.command(name='reset', pass_context=True, no_pm=True)
    async def rset(self, ctx):
        """
        resets to defaults
        """

        server = ctx.message.server
        self.init_server(server, True)
        await self.bot.say('Settings reset')

    @commands.command(pass_context=True, no_pm=True, name="exmboard")
    async def exmboard(self, ctx):
        """Leaderboard Stats"""

        server = ctx.message.server
        channel = ctx.message.channel

        if server.id not in self.settings:
            return
        if channel.id not in self.settings[server.id]['whitelist']:
            return

        await self.bot.send_typing(channel)
        try:
            await self.bot.say('LEADERBOARD TEST')
            for player in self.settings[server.id]['players']:
                await fetch_stats(self, ctx, player)
                #await self.bot.say(player)
        except Exception as e:
            #await self.bot.say("error: " + e.message + " -- " + e.args)
            err = e.message

    def __unload(self):
        self.session.close()

    async def send_cmd_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = self.bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)
        else:
            pages = self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await self.bot.send_message(ctx.message.channel, page)

async def fetch_stats(self, ctx, playername):
    url = "https://api.battlefieldtracker.com/api/v1/bfv/profile/origin/" + playername
    async with aiohttp.get(url) as response:
        return await self.bot.say(playername + " : " + int(response.status) + " : " + str(response))


#async def fetch_image(self, ctx, duser, urlen, user, platform):
#    async with aiohttp.get(urlen) as response:
#        if response.headers['Content-Type'] == "image/png":
#            return await self.bot.send_file(ctx.message.channel, io.BytesIO(await response.read()), filename=user + '.png')
#        else:
#            return await self.bot.say("Sorry " + duser.mention + ", could not find the player `"+ user + "`")

def setup(bot):
    pathlib.Path(path).mkdir(exist_ok=True, parents=True)
    bot.add_cog(ExmBoard(bot))