import discord
from discord.ext import commands
import pathlib
from cogs.utils.dataIO import dataIO
import aiohttp
import io
from .utils import checks
import json
import operator
import collections
from PIL import Image, ImageDraw, ImageFont
import urllib.request as urllib

path = 'data/exilium/exmboard/temp'
settings = dataIO.load_json(path + '/settings.json')
playerData = []

## main
for server in settings:
  print("Server: " + str(server) + "\n")
  for player in settings[server]['players']:
    print("Player: " + player + "\n")
    await playerData.append(await fetch_stats(player))

settings['playerData'] = playerData
dataIO.save_json(path + '/settings.json', settings)

## functions
async def fetch_stats(playername):
  url = "https://api.battlefieldtracker.com/api/v1/bfv/profile/origin/" + playername.replace(" ", "%20")
  print(" - URL: " + url + "\n")
  async with aiohttp.get(url) as response:
    return await response.json()