import pathlib
from cogs.utils.dataIO import dataIO
import aiohttp
import io
import json
import operator
import collections
import urllib.request as urllib
import asyncio

path = 'data/exilium/exmboard'
settings = dataIO.load_json(path + '/settings.json')
playerData = []

## functions
async def fetch_stats(playername):
  url = "https://battlefieldtracker.com/bfv/profile/origin/" + playername.replace(" ", "%20") + "/overview"
  print(" - URL: " + url + "\n")
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      responseString = await response.text()
      startPosSearchString = "window.__INITIAL_STATE__="
      startPos = responseString.find(startPosSearchString) + len(startPosSearchString)
      endPos = responseString.find(";", startPos)
      responseJson = json.loads(responseString[startPos:endPos])
      return responseJson["stats-v2"]["standardProfiles"]["bfv|origin|" + playername.lower()]

## main
async def main():
  try:
    for server in settings:
      print("Server: " + str(server) + "\n")
      for player in settings[server]['players']:
        print("Player: " + player + "\n")
        playerData.append(await fetch_stats(player))

      settings[server]['playerData'] = playerData

    dataIO.save_json(path + '/settings.json', settings)

  except Exception as e:
    print('ERROR: ' + e)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())