#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Sooo... these are my bots, will make a clean slate for u once I have time. -rbckman

import time
import logging
import requests
import subprocess
from datetime import datetime

def bot(log, botapi, botstatus, room, client):
    try: 
        lasthelp, lastradio, freqradio, freqhelp, lastsong = botstatus
    except:
        lastradio = time.time()
        freqradio = 3600
        lasthelp = time.time()
        freqhelp = 864000
        lastsong = ''
    msg = ''
    # put your bot scripts here! the ones here now are my bots, should make an empty plate for u.
    # if you need to get information from an api put the key in /.matrixchat/config.ini file like this
    # oou and bot script wont run without it at the moment
    # [botapi]
    # botapi = key
    
    #helpbot
    if time.time() - lasthelp > freqhelp or 'helpbot help' in log:
        msg = "helpbot: Hello! I'm helpbot, I come here as frequent as u want set freq [sec], I'm here to tell u aboot all awesome bots in this room, I let u guys introduce yourself\n"
        msg += "anetbot: Hello! I'm anet 3d printer, whats your name? run: [anetbot help] to see what u can do with me\n"
        msg += "bakerbot: Whatsup evybaady, I'm bakerbot, I keep track of how much energy goes into robs ryebreads, check me out with [bakerbot status] if you want to chack out a specific date try a date 2019-18-09\n"
        msg += "radiobot: Howdy bois and gals im radio bbtoyt help for mroe\n" 
        lasthelp = time.time()
    elif 'helpbot freq' in log:
        try:
            freqhelp = int(log.split("freq",1)[1])
            msg = 'helpbot: help frequensy set to ' + str(freqhelp) + ' sec'
        except:
            msg = 'helpbot: something funkky.. seconds right?'

    #anetbot
    elif 'anetbot help' in log:
        msg = "anetbot: Hello I'm Anet printer! [anet status] for my status" 
    elif 'anetbot status' in log: 
        progress = requests.get(url=botapi).json()
        try:
            hoursleft = str(int(progress['progress']['printTimeLeft']/60/60))
            minutesleft = str(int(progress['progress']['printTimeLeft']%3600/60))
            hoursprinted = str(int(progress['progress']['printTime']/60/60)) 
            minutesprinted = str(int(progress['progress']['printTime']%3600/60)) 
            msg = 'anetbot:'+str(progress['state'])+' model:'+(progress['job']['file']['name'])
            msg += ' time left: ' + hoursleft + ' h ' + minutesleft + ' min'
            msg += ' has been printing for: ' + hoursprinted + ' h ' + minutesprinted + ' min' 
            msg += ' is ' + str(int(progress['progress']['completion'])) + '% complete'
        except:
            msg = "anetbot: I'm currently offline, thanks for asking!"
            logging.exception('')
            pass

    #radiobot
    elif (time.time() - lastradio > freqradio) or ('radiobot status' in log):
        lastradio = time.time()
        try:
            newsong = subprocess.check_output(['/home/pi/rrr/nextsongs.sh']).decode().split('\n')
            if newsong[0] != lastsong:
                msg = 'radiobot: ' + newsong[0].replace('/media/robinsfirma/djsmellsfunny/','')
                msg += ' listen at http://radiorymd.com:8000/radiorymd'
                lastsong = newsong[0]
        except:
            msg = 'radiobot: not feeling ok, chack logs..'
            logging.exception('')
    elif 'radiobot skip' in log:
        try:
            o = subprocess.check_output(['/home/pi/rrr/skip.sh']).decode().split('\n')
            msg = 'radiobot: skipping song ' + o[0] + '\n'
        except:
            msg = 'radiobot: not good, chak logz'
            logging.exception('')
    elif 'radiobot freq' in log:
        try:
            freqradio = int(log.split("freq",1)[1])
            msg = 'radiobot: frequensy set to ' + str(freqradio) + ' sec'
        except:
            msg = 'radiobot: something funkky.. seconds right?'
            logging.exception('')
    elif 'radiobot help' in log:
        msg = 'radiobot: Hi, u can skip songs and set how freq Ill poll the radiostation'

    #bakerbot
    elif 'bakerbot help' in log:
        msg = "baekrbot: Hello I'm bakerbot! you can chec how many energiis goes into rye bread wit me! just pust status after mi name plz!" 
    elif 'bakerbot status' in log:
        try:
            year = int(log.split("status",1)[1][:5])
            month = int(log.split("status",1)[1][6:8])
            try:
                day = int(log.split("status",1)[1][9:11])
                date = str(year) + '-' + str(month) + '-' + str(day)
            except:
                day = 0
                date = str(year) + '-' + str(month)
        except:
            date = 'today'
            year = datetime.now().year
            month = datetime.now().month
            day = datetime.now().day
        try:
            cmd = '/home/pi/smartpick/smartpick.py'
            cmd2 = '/home/pi/smartpick/smartpick.py'
            o = subprocess.check_output([cmd, 'http://smartpi.local', '-y', str(year), '-m', str(month), '-d', str(day)]).decode().rstrip('\n')
            o2 = subprocess.check_output([cmd2, 'http://smartpi2.local', '-y', str(year), '-m', str(month), '-d', str(day)]).decode().rstrip('\n')
            msg = 'bakerbot: Owens and baking machines for ' + date + ': ' + o + ' Kwh\n'
            msg += 'other electronics: ' + o2 + ' Kwh\n'
            total = float(o) + float(o2)
            msg += 'Makes a grand total of: ' + str(total) + 'Kwh\n'
            if date == 'today':
                msg += 'If you want stats from a specific date you can do it like dis 2019-18-09, okay, thank you!'
        except:
            msg = "Baker bot is feeling bad today! check the logs.."
            logging.exception('')
            pass
    botstatus = lasthelp, lastradio, freqradio, freqhelp, lastsong
    return(msg, botstatus)
