#!/usr/bin/env python3

import asyncio
from os import path, utime
from datetime import date, timedelta
import aiohttp
from aiohttp import ClientSession
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
from sortedcontainers import SortedSet
from blinkpy.auth import BlinkTwoFARequiredError
import sys
import logging

async def inital_connect():
    blink = Blink(session=ClientSession())
    try:
        await blink.start()
    except BlinkTwoFARequiredError:
        await blink.prompt_2fa()

    return blink

async def connect(credentials):
    blink = Blink()
    auth = Auth(await json_load(credentials))
    blink.auth = auth
    try:
        await blink.start()
    except BlinkTwoFARequiredError:
        await blink.prompt_2fa()
    return blink

async def startup():
    # Expected to pass the name of the sync module in on the command line
    args = len(sys.argv) - 1

    syncmod ="" 
    localpath=""
    if (args < 2):
        syncmod = "Alice"
        localpath = "/home/schettj/blinkvideos"
    else: 
        syncmod= sys.argv[1]
        localpath = sys.argv[2]

    # set up logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(filename='blinkvideos.log', encoding='utf-8', level=logging.INFO)
    logging.info("start run: Syncmodue: "+syncmod+" Path: "+localpath)

    CREDENTIALS_FILE = "./blink.credentials.txt"
    if not path.isfile("./blink.credentials.txt"):
        blink = await inital_connect()
        await blink.save(CREDENTIALS_FILE)
    else:
        blink = await connect(CREDENTIALS_FILE)

    my_sync=blink.sync[syncmod]
    my_sync._local_storage["manifest"] = SortedSet()
    await my_sync.refresh()

    new_vid = await my_sync.check_new_videos()

    manifest = my_sync._local_storage["manifest"]
    
    # Download and delete all videos from sync module
    for item in reversed(manifest):
           await item.prepare_download(blink)
           videofile = f"{localpath}/{item.name}_{item.created_at.astimezone().isoformat().replace(':','_')}.mp4"
           await item.download_video( blink, videofile,)
           # make file mtime match video timestamp
           filetime = item.created_at.timestamp()
           logging.info(videofile)
           try:
               utime(videofile,(filetime,filetime))
           except:
               pass 
           await item.delete_video(blink)
           await asyncio.sleep(2)

asyncio.run(startup())

