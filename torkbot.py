#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Sooo... these are my bots, will make a clean slate for u once I have time. -rbckman

import time
import logging
import requests
import subprocess
import glob
import os
from datetime import datetime

def bot(log, botapi, botstatus, room, client):
    try: 
        laststatus, freqstatus, lastpic = botstatus
    except:
        laststatus = time.time()
        freqstatus = 3600
        lastpic = ''
    msg = ''
    # put your bot scripts here! the ones here now are my bots, should make an empty plate for u.
    # if you need to get information from an api put the key in /.matrixchat/config.ini file like this
    # oou and bot script wont run without it at the moment
    # [botapi]
    # botapi = key
  
    #torkbot
    if (time.time() - laststatus > freqstatus) or ('torkbot status' in log) or ('S' in log):
        laststatus = time.time()
        try:
            list_of_files = glob.glob('/home/pi/camera/*')
            newpic = max(list_of_files, key=os.path.getctime)
            if newpic != lastpic:
                with open('/home/pi/growbox.jpeg', 'rb') as image:
                    f = image.read()
                    imageurl = client.upload(f, 'image/jpeg', 'torken.jpeg')
                    room.send_image(imageurl, 'mmm')
                    lastpic = newpic
        except:
            msg = 'torkbot: not feeling ok, chack logs..'
            logging.exception('')
        try:
            with open('/home/pi/growbox/readings', 'r') as p:
                sensor = p.read().splitlines()[0]
        except:
            sensor = ''
        try:
            with open('/home/pi/growbox/fan', 'r') as f:
                fan = f.read().splitlines()[0]
        except:
            fan = ''
        try:
            with open('/home/pi/growbox/lights', 'r') as f:
                lights = f.read().splitlines()[0]
        except:
            lights = ''
        msg = 'torkbot: heres my status ' + sensor

    elif 'torkbot freq' in log:
        try:
            freqstatus = int(log.split("freq",1)[1])
            msg = 'torkbot: frequensy set to ' + str(freqstatus) + ' sec'
        except:
            msg = 'torkbot: something funkky.. seconds right?'
            logging.exception('')
    elif 'torkbot lights' in log:
        try:
            lightsstatus = log.split("lights",1)[1].strip()
            with open('/home/pi/growbox/lights', 'w') as f:
                f.write(lightsstatus)
            msg = 'torkbot: okey, turning lights ' + lightsstatus
        except:
            msg = 'torkbot: not feeling ok, chack logs..'
            logging.exception('')
    elif 'torkbot mist' in log:
        try:
            mist = log.split("mist",1)[1].strip()
            mist = mist.strip(' ')
            mist = mist.split(' ',1)
            with open('/home/pi/growbox/humidifier', 'w') as f:
                for a in mist:
                    f.write(a + '\n')
            msg = 'torkbot: okey, misting every ' + mist[0] + ' min for ' + mist[1] + ' seconds'
        except:
            msg = 'torkbot: needs to be intervall in minutes and then for how long in seconds'
            logging.exception('')
    elif 'torkbot fan' in log:
        try:
            fanstatus = log.split("fan",1)[1].strip()
            with open('/home/pi/growbox/fan', 'w') as f:
                f.write(fanstatus)
            msg = 'torkbot: okey, turning fan ' + fanstatus
        except:
            msg = 'torkbot: not feeling ok, chack logs..'
    elif 'torkbot help' in log:
        msg = 'torkbot: Hi, u can has shrooms, ask my status, turn on/off lights or fan'

    botstatus = laststatus, freqstatus, lastpic
    return(msg, botstatus)
